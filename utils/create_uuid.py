import uuid

def generate_uuid():
    return str(uuid.uuid4())

if __name__ == "__main__":
    print(generate_uuid())