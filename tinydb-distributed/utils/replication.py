
import requests

def replicate_data(other_node_url, data):

    

    try:

        response = requests.post(
            other_node_url,
            json=data
        )

        print("Replication success")

        return response.json()

    except Exception as e:

        print("Replication failed:", e)

        return None

