def success_response(msg):
    response = {
        "status":"success",
        "detail":msg,
    }
    return response

def error_response(msg):
    response = {
        "status":"error",
        "detail":msg,
    }
    return response