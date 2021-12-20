#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    logger.info("Downloading Artifact")
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    df = pd.read_csv(artifact_local_path)
    
    logger.info("Cleaning Data")

    # Filter Data to within Min and Max Price
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()

    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    #Drop rows not in proper geolocations
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()


    logger.info("Saving Data and Logging Artifact")

    df.to_csv("clean_sample.csv", index=False)

    artifact = wandb.Artifact(
        name=args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )

    artifact.add_file("clean_sample.csv")

    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Input artifact name in WandB",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Output artifact name in WandB",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Data type of output artifact",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description of Output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum price of Rental Data allowed in Dataset",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price of Rental Data allowed in Dataset",
        required=True
    )


    args = parser.parse_args()

    go(args)
