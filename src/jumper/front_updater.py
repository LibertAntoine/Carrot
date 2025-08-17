import re
import requests
from packaging.version import Version, InvalidVersion
from rest_framework.decorators import (
    api_view,
)
from rest_framework.response import Response
from django.conf import settings



@api_view(["GET"])
def check_update(request):
    try:
        versions = get_versions_from_jumper_repository()
        versions = apply_version_limitation(versions)

        if not versions:
            return Response()
        latest_version = max(versions, key=version_to_tuple)
        version_info = get_new_version_info(latest_version)
        return Response(version_info)
    except requests.RequestException as e:
        return Response({"error": str(e)}, status=500)


# Transform version string to tuple
def version_to_tuple(v):
    return tuple(int(x) for x in v.split("."))


def get_versions_from_jumper_repository():
    url = f"{settings.JUMPER_REPOSITORY_URL}/releases"
    response = requests.get(url)
    response.raise_for_status()  # raise error if HTTP code != 200
    releases = response.json()
    version_regex = re.compile(r"^\d+\.\d+\.\d+$")
    return [
        release["name"]
        for release in releases
        if "name" in release and version_regex.match(release["name"])
    ]

def apply_version_limitation(versions):
    version_limit = settings.MAX_ALLOWED_VERSION
    if not versions:
        return []

    print(f"Applying version limit: {version_limit}")
    limit_parts = version_limit.split(".")
    
    while len(limit_parts) < 3:
        limit_parts.append("999")
        
    limit_str = ".".join(limit_parts)
    limit_version = Version(limit_str)

    filtered_versions = []
    for v in versions:
        try:
            if Version(v) <= limit_version:
                filtered_versions.append(v)
        except InvalidVersion:
            pass
    return filtered_versions



def get_new_version_info(version_tag):
    url = f"https://github.com/LibertAntoine/Jumper/releases/download/{version_tag}/latest.json"
    response = requests.get(url)
    response.raise_for_status()  # raise error if HTTP code != 200
    return response.json()


