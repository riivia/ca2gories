import json
from base64 import urlsafe_b64encode, urlsafe_b64decode
from zlib import compress, decompress

# Created with the help of ChatGPT

def obfuscate(data):
    # Serialize the data to a JSON string
    json_str = json.dumps(data)
    
    # Compress the JSON string using zlib (since zlib might be more efficient for short strings)
    compressed_bytes = compress(json_str.encode('utf-8'))
    
    # Encode the compressed bytes to base64 (URL-safe)
    base64_encoded = urlsafe_b64encode(compressed_bytes)
    
    # Convert the base64 bytes to a string
    encoded_str = base64_encoded.decode('utf-8')
    
    return encoded_str


def unobfuscate(encoded_str):
    try:
        # Decode the base64 string
        base64_bytes = encoded_str.encode('utf-8')
    
        # Ensure proper padding by adding '=' characters if needed
        padded_length = len(base64_bytes) + (4 - len(base64_bytes) % 4) % 4
        base64_padded = base64_bytes.ljust(padded_length, b'=')

        # Decode base64 (URL-safe) to get compressed bytes
        compressed_bytes = urlsafe_b64decode(base64_padded)
        
        # Decompress the bytes using zlib
        decompressed_bytes = decompress(compressed_bytes)
        
        # Decode JSON
        json_str = decompressed_bytes.decode('utf-8')
        data = json.loads(json_str)
        
        return data
    
    except Exception as e:
        print(f"Error during unobfuscation: {e}")
        
        return None
