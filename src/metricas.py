import numpy as np


def mae(y_real, y_prev):
    """Erro absoluto médio, em dólares."""
    y_real = np.array(y_real)
    y_prev = np.array(y_prev)
    erros = np.abs(y_prev - y_real) 
    return erros.mean() 

def rmse(y_real, y_prev):
    """Raíz do erro quadrátio médio, em dólares."""
    y_real = np.array(y_real)
    y_prev = np.array(y_prev)
    erros = (y_prev - y_real) 
    quadrados = (erros)**2
    media = quadrados.mean()
    return np.sqrt(media) 

def mape(y_real, y_prev):
    """Erro percentual absoluto médio, em %."""
    y_real = np.array(y_real)
    y_prev = np.array(y_prev)
    erros = np.abs(y_prev - y_real) 
    erros_relativos = erros/y_real 
    media_relativa = erros_relativos.mean()
    porcentagem = media_relativa * 100
    return porcentagem 

def metricas(y_real, y_prev):
    """Devolve as três métricas em um dicionário."""
    return {
        "MAE": float(mae(y_real, y_prev)),
        "RMSE": float(rmse(y_real, y_prev)),
        "MAPE_%": float(mape(y_real, y_prev)),
    }