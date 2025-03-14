from math import sin, cos, tan, asin, atan, atan2, sqrt, radians

WGS84 = {
    "a": 6378137.0,
    "b": 6356752.314245,
    "f": 1 / 298.257223563,
}

GCJ02 = {
    "a": 6378137.0,
    "b": 6356752.314140,
    "f": 1 / 298.257222101,
}


def haversine(lng1, lat1, lng2, lat2):
    """Calculate distance according to Haversine formula"""
    R = 6371 # km
    delta_lat = radians(lat2 - lat1)
    delta_lng = radians(lng2 - lng1)
    a = (1 - cos(delta_lat) + cos(lat1) * cos(lat2) * (1 - cos(delta_lng))) / 2
    return 2 * R * asin(sqrt(a))


# Ref: https://www.movable-type.co.uk/scripts/latlong-vincenty.html
def vincenty(lng1, lat1, lng2, lat2, params, tol=1e-12):
    """Calculate distance according to Vincenty's formulae"""
    lng1 = radians(lng1)
    lat1 = radians(lat1)
    lng2 = radians(lng2)
    lat2 = radians(lat2)

    U1 = atan((1 - params["f"]) * tan(lat1))
    U2 = atan((1 - params["f"]) * tan(lat2))
    L = lng2 - lng1

    SIN_U1 = sin(U1)
    COS_U1 = cos(U1)
    SIN_U2 = sin(U2)
    COS_U2 = cos(U2)

    lam = L
    for _ in range(100):
        sin_lam = sin(lam)
        cos_lam = cos(lam)

        sin_sigma = sqrt((COS_U2 * sin_lam) ** 2 + (COS_U1 * SIN_U2 - SIN_U1 * COS_U2 * cos_lam) ** 2)
        cos_sigma = SIN_U1 * SIN_U2 + COS_U1 * COS_U2 * cos_lam
        sigma = atan2(sin_sigma, cos_sigma)

        sin_alpha = COS_U1 * COS_U2 * sin_lam / sin_sigma
        cos_sq_alpha = 1 - sin_alpha ** 2
        cos_2sigma_m = cos_sigma - 2 * SIN_U1 * SIN_U2 / cos_sq_alpha

        C = params["f"] / 16 * cos_sq_alpha * (4 + params["f"] * (4 - 3 * cos_sq_alpha))
        last_lam = lam
        lam = L + (1 - C) * params["f"] * sin_alpha * (sigma + C * sin_sigma * (cos_2sigma_m + C * cos_sigma * (-1 + 2 * cos_2sigma_m ** 2)))

        if abs(lam - last_lam) <= tol:
            break

    u_sq = cos_sq_alpha * (params["a"] ** 2 - params["b"] ** 2) / params["b"] ** 2
    A = 1 + u_sq / 16384 * (4096 + u_sq * (-768 + u_sq * (320 - 175 * u_sq)))
    B = u_sq / 1024 * (256 + u_sq * (-128 + u_sq * (74 - 47 * u_sq)))
    delta_sigma = B * sin_sigma * (
        cos_2sigma_m + B / 4 * (
            cos_sigma * (-1 + 2 * cos_2sigma_m ** 2)
            - B / 6 * cos_2sigma_m * (-3 + 4 * sin_sigma ** 2) * (-3 + 4 * cos_2sigma_m ** 2)
        )
    )
    s = params["b"] * A * (sigma - delta_sigma)
    return s
