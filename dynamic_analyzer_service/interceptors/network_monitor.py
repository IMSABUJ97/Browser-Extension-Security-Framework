
def log_network_request(request, log_list):
    if request.resource_type in ["xhr", "fetch"]:
        log_list.append({
            "url": request.url,
            "method": request.method,
            "type": request.resource_type
        })