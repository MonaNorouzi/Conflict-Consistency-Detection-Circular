from fastapi import APIRouter

router = APIRouter()


@router.get("/rules")
def list_rules() -> dict[str, list[str]]:
    return {"rules": ["Basel III", "AML-KYC", "Consumer Protection"]}
