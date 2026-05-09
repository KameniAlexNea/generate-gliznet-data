class Config:
    MAX_INPUT_TOKENS = 2048 * 3
    EXAMPLES_PER_BUNDLE = 5
    MIN_NUM_LABELS = 1
    MIN_TEXT_LENGTH = 30
    MAX_OUTPUT_TOKENS = 4096

    # Label vocabulary size per bundle
    NUM_LABELS = 15

    # How many labels are assigned as positive / negative per text.
    # Skew toward more negatives to match real-world class imbalance.
    POSITIVE_LABELS_MIN = 1
    POSITIVE_LABELS_MAX = 5
    NEGATIVE_LABELS_MIN = 8
    NEGATIVE_LABELS_MAX = 15
