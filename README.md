# Splitter
A web app for uploading an image of a receipt and calculating who owes what using AWS Rekognition.

### Concerns:
1. On creation of a receipt, processes image
- Create microservice to process images to limit web resources
2. Caching receipt properties
- Is it better to maybe just save them as properties?