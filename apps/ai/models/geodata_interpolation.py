from scipy.interpolate import griddata

def interpolate_points(xy, values, xi):
    return griddata(xy, values, xi, method='linear')
