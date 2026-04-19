from fastapi import HTTPException, status

not_found = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No encontrado")
forbidden = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permiso")
credentials_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciales inválidas",
    headers={"WWW-Authenticate": "Bearer"},
)
inactive_user = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
