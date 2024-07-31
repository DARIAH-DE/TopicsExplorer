/**
 * Bag-of-words representation of a text document.
 */
export type BagOfWords = { name: string; counts: Map<number, number> };

/**
 * Might be a value of type T or undefined.
 */
export type Maybe<T> = T | undefined;

/**
 * Might be a value of type T or null.
 */
export type Nullable<T> = T | null;
