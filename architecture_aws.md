## Architecture diagram

> GitHub supports Mermaid diagrams in markdown. If your viewer doesn't render Mermaid, scroll down for text diagram.

flowchart LR
User[User (Browser / Frontend)] -->|Upload image / text| ALB[ALB / API Gateway]
ALB --> ECS[Fargate / EC2 (Flask API)]
ALB --> S3[Amazon S3 (uploads bucket)]
ECS -->|Put/Get| S3
ECS -->|Call| Textract[Amazon Textract]
ECS -->|Call| Rekognition[Amazon Rekognition (optional)]
ECS -->|Call| Bedrock[Amazon Bedrock (LLM fallback)]
ECS -->|PutItem / GetItem| DynamoDB[Amazon DynamoDB (feedback)]
ECS -->|Read| KB[S3 (KB JSON) or DynamoDB KB]
Batch[Batch / Lambda (batch processor)] --> S3
S3 -->|S3 Event ->| LambdaTrigger[AWS Lambda (S3 trigger)]
LambdaTrigger --> ECS
CloudWatch[CloudWatch Logs & Metrics] <-- ECS
CloudWatch <-- LambdaTrigger

```
flowchart LR
User[User (Browser / Frontend)] -->|Upload image / text| ALB[ALB / API Gateway]
ALB --> ECS[Fargate / EC2 (Flask API)]
ALB --> S3[Amazon S3 (uploads bucket)]
ECS -->|Put/Get| S3
ECS -->|Call| Textract[Amazon Textract]
ECS -->|Call| Rekognition[Amazon Rekognition (optional)]
ECS -->|Call| Bedrock[Amazon Bedrock (LLM fallback)]
ECS -->|PutItem / GetItem| DynamoDB[Amazon DynamoDB (feedback)]
ECS -->|Read| KB[S3 (KB JSON) or DynamoDB KB]
Batch[Batch / Lambda (batch processor)] --> S3
S3 -->|S3 Event ->| LambdaTrigger[AWS Lambda (S3 trigger)]
LambdaTrigger --> ECS
CloudWatch[CloudWatch Logs & Metrics] <-- ECS
CloudWatch <-- LambdaTrigger
```
