import math

pi = math.pi

def Volum(lng, d):
    r = float(d)/200
    l = float(lng)

    v = pi *(r**2) *l

    return round(v,3) 