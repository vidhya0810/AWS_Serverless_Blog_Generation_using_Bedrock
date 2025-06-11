import boto3
import botocore.config 
import json
from datetime import datetime

def blog_generate_using_bedrock(blogtopic:str)-> str:
    """
    Generate a blog post using Amazon Bedrock.
    
    Args:
        blogtopic (str): The topic of the blog post to generate.
        
    Returns:
        str: The generated blog post content.
    """
    prompt = f"""<s>[INST]Human: Write a 200 word blog post on the topic: {blogtopic}
    Assistant: [/INST]"""
    
    body ={
        "prompt": prompt,
        "max_tokens": 200,
        "temperature": 0.5,
        "top_p": 0.9,
        "top_k": 50
        
    }
    
    try:
        bedrock=boto3.client("bedrock-runtime", region_name = "ap-southeast-2",
                             config = botocore.config.Config(
                               read_timeout=300,
                               retries={'max_attempts':3}  
                             ))
        response = bedrock.invoke_model(
            modelId="mistral.mistral-7b-instruct-v0:2",
            body=json.dumps(body)
        )
        
        response_content = response.get("body").read()
        response_data = json.loads(response_content)
        print(response_data)
        blog_details = response_data["generation"]
        return blog_details
    except Exception as e:
        print(f"Error generating blog post: {e}")
        return "An error occurred while generating the blog post."

def save_blog_to_s3(blog_content: str, s3_key: str, s3_bucket: str):
    """
    Save the generated blog content to an S3 bucket.
    
    Args:
        blog_content (str): The content of the blog post to save.
        s3_key (str): The S3 key where the blog post will be saved.
        s3_bucket (str): The name of the S3 bucket.
    """
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=blog_content)
        print(f"Blog post saved to s3://{s3_bucket}/{s3_key}")
    except Exception as e:
        print(f"Error saving blog post to S3: {e}")


def lambda_handler(event, context):
    # TODO implement
    event = json.loads(event["body"])
    blogtopic = event['blog_topic']
    
    generate_blog= blog_generate_using_bedrock(blogtopic=blogtopic)
    
    if generate_blog:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        s3_key = f"blog-output/{current_time}.txt"
        s3_bucket= "aws_bedrock_blogs_generated"
        save_blog_to_s3(blog_content=generate_blog, s3_key=s3_key, s3_bucket=s3_bucket)
        
        
    else:
        print("No blog generated")
        
    return {
        'statusCode': 200,
        'body': json.dumps("Blog generation completed successfully.")}
        
