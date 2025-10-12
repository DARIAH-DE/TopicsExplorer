#![allow(clippy::needless_range_loop)]

mod lda;

use lda::{train_lda, LdaHyperparameters, LdaResult, TextDocument};
use tauri::AppHandle;

#[tauri::command]
async fn train_model(
    app: AppHandle,
    docs: Vec<TextDocument>,
    params: Option<LdaHyperparameters>,
) -> Result<LdaResult, String> {
    if docs.is_empty() {
        return Err("No documents provided".into());
    }
    train_lda(Some(&app), docs, params.unwrap_or_default()).map_err(|e| e.to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![train_model])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
