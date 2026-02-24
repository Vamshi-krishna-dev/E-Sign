from fastapi import Header, HTTPException

def require_admin(x_role: str = Header("user")):
    """
    Allow only admin and superadmin to call this endpoint.
    Borrowers (user role) cannot confirm disbursement.
    """
    if x_role.lower() not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Admin privileges required"
        )
    return True