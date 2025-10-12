# Explore your text collection with a topic model

Topic models discover the main themes in a collection of text documents. They automatically find recurring topics by looking at which words tend to appear together. Each document is represented as a mix of these topics and lists the most characteristic words for each.

This application provides a simple and intuitive interface for exploring your own text corpus using **latent Dirichlet allocation**, one of the most popular topic models.

> [!IMPORTANT]  
> Version 3 is currently under development and will be a complete reimplementation.

## Setup

Install Node.js and Rust with `mise`:

```
$ mise install
```

then the project dependencies:

```
$ npm ci
```
