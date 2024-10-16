#!/bin/bash

# Function to initialize sparse checkout, excluding the data/raw folder
initial_clone() {
  REPO_URL=$1
  TARGET_DIR=$2

  # Clone the repository with sparse checkout enabled
  git clone --filter=blob:none --no-checkout "$REPO_URL" "$TARGET_DIR"
  cd "$TARGET_DIR"

  # Enable sparse checkout and exclude the data/raw folder
  git sparse-checkout init --cone
  git sparse-checkout set '/src' '/data/interim' '/data/processed' '/data/stats' '!data/raw'
  git checkout
}

# Function to download specific subfolder from data/raw
download_subfolder() {
  SUBFOLDER=$1
  git sparse-checkout add "data/raw/$SUBFOLDER"
  git checkout
}

# Function to clean up downloaded subfolder after processing
cleanup_subfolder() {
  SUBFOLDER=$1
  escaped_path=$(echo $SUBFOLDER | sed 's/\//\\\//g')
  sed -i /$escaped_path/d .git/info/sparse-checkout
  rm -rf "data/raw/$SUBFOLDER"
  git sparse-checkout reapply
}

# Main script logic
case $1 in
  clone)
    if [ $# -ne 3 ]; then
      echo "Usage: $0 clone <repo_url> <target_dir>"
      exit 1
    fi
    initial_clone $2 $3
    ;;
  download)
    if [ $# -ne 2 ]; then
      echo "Usage: $0 download <subfolder>"
      exit 1
    fi
    download_subfolder $2
    ;;
  cleanup)
    if [ $# -ne 2 ]; then
      echo "Usage: $0 cleanup <subfolder>"
      exit 1
    fi
    cleanup_subfolder $2
    ;;
  *)
    echo "Usage: $0 {clone|download|cleanup}"
    exit 1
    ;;
esac

