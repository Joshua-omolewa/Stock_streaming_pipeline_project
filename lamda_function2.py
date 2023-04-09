import requests
import json

def del_all_livy_batches(livy_endpoint):
    """
    This function deletes all spark job runining in the EMR cluster
    """
    batches_endpoint = f"{livy_endpoint}/batches"
    
    try:
        # Get the list of all batches
        #sample payload from livy {"from":0,"total":1,"sessions":[{"id":19,"name":"josh-stream-app","owner":null}
        response = requests.get(batches_endpoint)
        response.raise_for_status() #to check request was successful
        batches = response.json()["sessions"]
        
        # Delete all the batches
        for batch in batches:
            batch_id = batch["id"]
            batch_url = f"{batches_endpoint}/{batch_id}"
            response = requests.delete(batch_url)
            response.raise_for_status() #to check request was successful
        
        return {"message": "All Livy batches deleted successfully!"}
    
    except requests.exceptions.RequestException as e:
        error_msg = f"Error deleting Livy batches: {e}"
        print(error_msg)
        return {"error": error_msg}