use ahash::RandomState;
use anyhow::Result;
use itertools::Itertools;
use rand::prelude::*;
use rand::SeedableRng;
use rayon::prelude::*;
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Mutex;
use tauri::{AppHandle, Emitter};

#[derive(Debug, Deserialize)]
pub struct TextDocument {
    pub text: String,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct LdaHyperparameters {
    pub num_topics: usize,
    pub num_iterations: usize,
    pub alpha: f64,
    pub beta: f64,
    pub seed: Option<u64>,
}

impl Default for LdaHyperparameters {
    fn default() -> Self {
        Self {
            num_topics: 10,
            num_iterations: 1000,
            alpha: 0.1,
            beta: 0.01,
            seed: None,
        }
    }
}

#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ProgressEvent {
    pub iteration: usize,
    pub log_likelihood: f64,
    pub perplexity: f64,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct LdaResult {
    pub theta: Option<Vec<Vec<f64>>>,
    pub phi: Option<Vec<Vec<f64>>>,
    pub topics: Vec<Topic>,
    pub vocab: Vec<String>,
    pub stopwords: Vec<String>,
    pub total_tokens: usize,
    pub log_likelihood: f64,
    pub perplexity: f64,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Topic {
    pub topic_index: usize,
    pub top_words: Vec<WordProb>,
    pub dominance_score: f64,
}

#[derive(Debug, Serialize)]
pub struct WordProb {
    pub word: String,
    pub prob: f64,
}

pub fn train_lda(
    app: Option<&AppHandle>,
    text_documents: Vec<TextDocument>,
    settings: LdaHyperparameters,
) -> Result<LdaResult> {
    let tokenized: Vec<Vec<String>> = preprocess_text_documents(&text_documents)?;
    let (vocab, corpus, doc_lengths, stopwords) = build_corpus(tokenized)?;

    let d: usize = corpus.len();
    let v: usize = vocab.len();
    if v == 0 {
        anyhow::bail!("Empty vocabulary after preprocessing (possibly all words were stopwords).");
    }

    let k: usize = settings.num_topics;
    let alpha: f64 = settings.alpha;
    let beta: f64 = settings.beta;
    let num_iterations: usize = settings.num_iterations;

    let ndk: Vec<Vec<AtomicUsize>> = (0..d)
        .map(|_| (0..k).map(|_| AtomicUsize::new(0)).collect())
        .collect();
    let nkw: Vec<Vec<AtomicUsize>> = (0..k)
        .map(|_| (0..v).map(|_| AtomicUsize::new(0)).collect())
        .collect();
    let nk: Vec<AtomicUsize> = (0..k).map(|_| AtomicUsize::new(0)).collect();
    let z_assignments: Vec<Mutex<Vec<usize>>> = (0..d).map(|_| Mutex::new(Vec::new())).collect();

    let mut rng = if let Some(seed) = settings.seed {
        rand_pcg::Pcg64Mcg::seed_from_u64(seed)
    } else {
        rand_pcg::Pcg64Mcg::from_entropy()
    };

    let num_threads = rayon::current_num_threads();
    let rngs: Vec<Mutex<rand_pcg::Pcg64Mcg>> = (0..num_threads)
        .map(|_| Mutex::new(rand_pcg::Pcg64Mcg::seed_from_u64(rng.gen())))
        .collect();

    corpus.par_iter().enumerate().for_each(|(di, doc)| {
        let thread_index = rayon::current_thread_index().unwrap_or(0) % num_threads;
        let mut local_rng = rngs[thread_index].lock().unwrap();
        let mut z_for_doc: Vec<usize> = Vec::with_capacity(doc.len());
        for &w in doc.iter() {
            let z: usize = local_rng.gen_range(0..k);
            z_for_doc.push(z);
            ndk[di][z].fetch_add(1, Ordering::Relaxed);
            nkw[z][w].fetch_add(1, Ordering::Relaxed);
            nk[z].fetch_add(1, Ordering::Relaxed);
        }
        *z_assignments[di].lock().unwrap() = z_for_doc;
    });

    let v_beta: f64 = (v as f64) * beta;

    if let Some(app) = app {
        let (ll, n_tokens) = log_likelihood_from_counts(
            &corpus,
            &ndk,
            &nkw,
            &nk,
            &doc_lengths,
            alpha,
            beta,
            v,
        );
        let perp = f64::exp(-ll / (n_tokens as f64));

        let _ = app.emit(
            "lda:progress",
            ProgressEvent {
                iteration: 0,
                log_likelihood: ll,
                perplexity: perp,
            },
        );
    }

    for iter in 0..num_iterations {
        corpus.par_iter().enumerate().for_each(|(d_i, doc)| {
            let thread_index = rayon::current_thread_index().unwrap_or(0) % num_threads;
            let mut local_rng = rngs[thread_index].lock().unwrap();
            let mut z_assignments_local = z_assignments[d_i].lock().unwrap();
            let doc_z = &mut *z_assignments_local;
            for (pos, &w) in doc.iter().enumerate() {
                let z_old = doc_z[pos];
                ndk[d_i][z_old].fetch_sub(1, Ordering::Relaxed);
                nkw[z_old][w].fetch_sub(1, Ordering::Relaxed);
                nk[z_old].fetch_sub(1, Ordering::Relaxed);

                let mut probs: Vec<f64> = vec![0f64; k];
                let mut sum = 0f64;
                for z in 0..k {
                    let left: f64 = ndk[d_i][z].load(Ordering::Relaxed) as f64 + alpha;
                    let right_num: f64 = nkw[z][w].load(Ordering::Relaxed) as f64 + beta;
                    let denom = nk[z].load(Ordering::Relaxed) as f64 + v_beta;
                    let p: f64 = left * (right_num / denom);
                    probs[z] = p;
                    sum += p;
                }

                let u: f64 = local_rng.gen::<f64>() * sum;
                let mut acc: f64 = 0f64;
                let mut z_new: usize = 0usize;
                for z in 0..k {
                    acc += probs[z];
                    if u <= acc {
                        z_new = z;
                        break;
                    }
                }
                doc_z[pos] = z_new;
                ndk[d_i][z_new].fetch_add(1, Ordering::Relaxed);
                nkw[z_new][w].fetch_add(1, Ordering::Relaxed);
                nk[z_new].fetch_add(1, Ordering::Relaxed);
            }
        });

        if let Some(app) = app {
            if (iter + 1) % 10 == 0 {
                let (ll, n_tokens) = log_likelihood_from_counts(
                    &corpus,
                    &ndk,
                    &nkw,
                    &nk,
                    &doc_lengths,
                    alpha,
                    beta,
                    v,
                );
                let perp = f64::exp(-ll / (n_tokens as f64));

                let _ = app.emit(
                    "lda:progress",
                    ProgressEvent {
                        iteration: iter + 1,
                        log_likelihood: ll,
                        perplexity: perp,
                    },
                );
            }
        }
    }

    let mut phi: Vec<Vec<f64>> = vec![vec![0f64; v]; k];
    let mut theta: Vec<Vec<f64>> = vec![vec![0f64; k]; d];

    phi.par_iter_mut().enumerate().for_each(|(z, phi_row)| {
        let denom = nk[z].load(Ordering::Relaxed) as f64 + v_beta;
        for w in 0..v {
            phi_row[w] = (nkw[z][w].load(Ordering::Relaxed) as f64 + beta) / denom;
        }
    });

    theta
        .par_iter_mut()
        .enumerate()
        .for_each(|(d_i, theta_row)| {
            let doc_len = doc_lengths[d_i] as f64;
            for z in 0..k {
                theta_row[z] = (ndk[d_i][z].load(Ordering::Relaxed) as f64 + alpha)
                    / (doc_len + (k as f64) * alpha);
            }
        });

    let mut dominance_scores: Vec<f64> = vec![0.0; k];
    for di in 0..d {
        for z in 0..k {
            dominance_scores[z] += theta[di][z];
        }
    }

    let total_dominance: f64 = dominance_scores.iter().sum();
    for score in dominance_scores.iter_mut() {
        *score /= total_dominance;
    }

    let top_n: usize = 50.min(v.max(1));
    let mut topics: Vec<Topic> = Vec::with_capacity(k);
    topics.par_extend((0..k).into_par_iter().map(|z| {
        let mut pairs: Vec<(usize, f64)> = (0..v).map(|w| (w, phi[z][w])).collect();
        pairs.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
        let top_words: Vec<WordProb> = pairs
            .into_iter()
            .take(top_n)
            .map(|(w, p)| WordProb {
                word: vocab[w].clone(),
                prob: p,
            })
            .collect();
        Topic {
            topic_index: z,
            top_words,
            dominance_score: dominance_scores[z],
        }
    }));

    topics.sort_by(|a, b| b.dominance_score.partial_cmp(&a.dominance_score).unwrap());

    let (ll, total_tokens) = log_likelihood(&corpus, &theta, &phi);
    let perp: f64 = f64::exp(-ll / (total_tokens as f64));

    Ok(LdaResult {
        theta: Some(theta),
        phi: Some(phi),
        topics,
        vocab,
        stopwords,
        total_tokens: total_tokens,
        log_likelihood: ll,
        perplexity: perp,
    })
}

fn preprocess_text_documents(text_documents: &Vec<TextDocument>) -> Result<Vec<Vec<String>>> {
    let re: Regex = Regex::new(r"\w+")?;
    let min_token_len: usize = 2;
    let mut out: Vec<Vec<String>> = Vec::with_capacity(text_documents.len());
    for d in text_documents {
        let mut toks: Vec<String> = Vec::new();
        for m in re.find_iter(&d.text) {
            let t: String = m.as_str().to_ascii_lowercase();
            if t.len() >= min_token_len {
                toks.push(t);
            }
        }
        out.push(toks);
    }
    Ok(out)
}

fn build_corpus(
    tokenized: Vec<Vec<String>>,
) -> Result<(Vec<String>, Vec<Vec<usize>>, Vec<usize>, Vec<String>)> {
    let mut global_counts: HashMap<String, usize, RandomState> =
        HashMap::with_hasher(RandomState::new());
    for doc in tokenized.iter() {
        for t in doc {
            *global_counts.entry(t.clone()).or_insert(0) += 1;
        }
    }

    let mut pairs: Vec<(String, usize)> = global_counts.iter().map(|(k, v)| (k.clone(), *v)).collect();
    pairs.sort_by(|a, b| b.1.cmp(&a.1));
    let most_common_words: usize = 100.min(pairs.len());
    let stopwords_set: HashSet<String> = pairs
        .iter()
        .take(most_common_words)
        .map(|(w, _)| w.clone())
        .collect();
    let stopwords: Vec<String> = stopwords_set.iter().cloned().sorted().collect::<Vec<_>>();

    let mut vocab_map: HashMap<String, usize, RandomState> =
        HashMap::with_hasher(RandomState::new());
    for doc in tokenized.iter() {
        for t in doc {
            if stopwords_set.contains(t) {
                continue;
            }
            if global_counts.get(t).unwrap_or(&0) < &3 {
                continue;
            }
            if !vocab_map.contains_key(t) {
                let id = vocab_map.len();
                vocab_map.insert(t.clone(), id);
            }
        }
    }

    let mut vocab: Vec<String> = vec!["".to_string(); vocab_map.len()];
    for (w, &i) in vocab_map.iter() {
        vocab[i] = w.clone();
    }

    let mut corpus: Vec<Vec<usize>> = Vec::with_capacity(tokenized.len());
    let mut doc_lengths: Vec<usize> = Vec::with_capacity(tokenized.len());
    for doc in tokenized.iter() {
        let mut ids = Vec::new();
        for t in doc {
            if let Some(&id) = vocab_map.get(t) {
                ids.push(id);
            }
        }
        doc_lengths.push(ids.len());
        corpus.push(ids);
    }

    Ok((vocab, corpus, doc_lengths, stopwords))
}

fn log_likelihood(
    corpus: &Vec<Vec<usize>>,
    theta: &Vec<Vec<f64>>,
    phi: &Vec<Vec<f64>>,
) -> (f64, usize) {
    let d: usize = corpus.len();
    let k: usize = phi.len();
    let mut ll: f64 = 0f64;
    let mut n: usize = 0usize;
    for di in 0..d {
        for &w in corpus[di].iter() {
            let mut pw = 0f64;
            for z in 0..k {
                pw += theta[di][z] * phi[z][w];
            }
            if pw > 0.0 {
                ll += pw.ln();
            }
            n += 1;
        }
    }
    (ll, n)
}

fn log_likelihood_from_counts(
    corpus: &Vec<Vec<usize>>,
    ndk: &Vec<Vec<AtomicUsize>>,
    nkw: &Vec<Vec<AtomicUsize>>,
    nk: &Vec<AtomicUsize>,
    doc_lengths: &Vec<usize>,
    alpha: f64,
    beta: f64,
    v: usize,
) -> (f64, usize) {
    let k: usize = nk.len();
    let v_beta: f64 = (v as f64) * beta;
    let mut ll: f64 = 0f64;
    let mut n: usize = 0usize;

    let denom_right: Vec<f64> = (0..k)
        .map(|z| nk[z].load(Ordering::Relaxed) as f64 + v_beta)
        .collect();

    for (di, doc) in corpus.iter().enumerate() {
        let denom_left = doc_lengths[di] as f64 + (k as f64) * alpha;
        for &w in doc.iter() {
            let mut pw = 0f64;
            for z in 0..k {
                let left = (ndk[di][z].load(Ordering::Relaxed) as f64 + alpha) / denom_left;
                let right = (nkw[z][w].load(Ordering::Relaxed) as f64 + beta) / denom_right[z];
                pw += left * right;
            }
            if pw > 0.0 {
                ll += pw.ln();
            }
            n += 1;
        }
    }
    (ll, n)
}
