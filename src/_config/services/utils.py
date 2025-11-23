def get_full_domain_from_request(request):
    host = request.META.get("HTTP_X_FORWARDED_HOST", "") or request.META.get(
        "HTTP_HOST", "localhost"
    )
    scheme = "https://" if request.is_secure() else "http://"
    return f"{scheme}{host}"
