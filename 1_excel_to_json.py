import os  
import time  
import requests  
import json  
from dotenv import load_dotenv  
from pathlib import Path  
  
# Load environment variables from .env file  
load_dotenv()  
adi_endpoint = os.getenv("ADI_ENDPOINT")  
adi_api_key = os.getenv("ADI_API_KEY")  
adi_model_id = "prebuilt-layout"  

print(adi_endpoint)

# Define the headers for the ADI API request  
headers = {  
    "Content-Type":  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # Adjust based on your image format (e.g., image/jpeg)  
    "Ocp-Apim-Subscription-Key": adi_api_key,  
}  
  
def call_api(file_path, extracted_text_file_path):  
    with open(file_path, "rb") as file:  
        document_data = file.read()  
  
    url = f"{adi_endpoint}documentintelligence/documentModels/prebuilt-layout:analyze?api-version=2024-11-30&outputContentFormat=markdown"
    
    response = requests.post(url, headers=headers, data=document_data)  
  
    if response.status_code == 202:  
        result_url = response.headers["Operation-Location"]  
        while True:  
            result_response = requests.get(result_url, headers={"Ocp-Apim-Subscription-Key": adi_api_key})  
            result_status = result_response.status_code  
            result_data = result_response.json()  
  
            if result_status == 200 and result_data.get("status") == "succeeded":  
                with open(extracted_text_file_path, "w") as json_file:  
                    json.dump(result_data, json_file, indent=2)  
                print(f"Processing of '{file_path.name}' succeeded. Result saved to '{extracted_text_file_path.name}'")  
                break  
            elif result_data.get("status") == "failed":  
                print(f"Document processing failed for '{file_path.name}'.")  
                break  
            else:  
                print(f"Processing '{file_path.name}'... Waiting for 5 seconds before retrying.")  
                time.sleep(5)  
    else:  
        print(f"Failed to start processing the document '{file_path.name}': {response.status_code}")  
        print(response.text)  
  
def main():  
    # Directories  
    files_dir = Path("input_documents")  
    output_dir = Path("content_json")  
    output_dir.mkdir(parents=True, exist_ok=True)  
  
    # Check if input directory exists  
    if not files_dir.exists():  
        print(f"Input directory '{files_dir}' does not exist.")  
        return  
  
    # List all documents in the input directory  
    document_files = list(files_dir.glob("*.*"))  
    if not document_files:  
        print(f"No files found in '{files_dir}'.")  
        return  
  
    # Process each input document  
    for document_file in document_files:  
        # Define output JSON filename  
        json_filename = f"{document_file.stem}.json"  
        json_output_path = output_dir / json_filename  
  
        print(f"Processing file '{document_file.name}'...")  
        call_api(document_file, json_output_path)  
  
if __name__ == "__main__":  
    main()  