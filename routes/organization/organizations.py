from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File, Query
from applications.organization.models import Organization
from applications.user.models import User
from applications.subscription.models import Subscription



router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/{organization_id}/users")
async def list_organization_users(organization_id: int):
    organization = await Organization.get_or_none(id=organization_id).prefetch_related("users")
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    if not organization.users:
        return []
    users = organization.users
    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active
        }
        for user in users
    ]


@router.get("/{organization_id}")
async def get_organization_details(organization_id: int):
    organization = await Organization.get_or_none(id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return {
        "id": organization.id,
        "name": organization.name,
        "is_active": organization.is_active,
        "created_at": organization.created_at
    }


@router.post("/create-organization")
async def create_organization(
    name: str = Form(...),
):
    existing_org = await Organization.get_or_none(name=name)
    if existing_org:
        raise HTTPException(status_code=400, detail="Organization with this name already exists")

    organization = await Organization.create(
        name=name
    )
    return {
        "id": organization.id,
        "name": organization.name,
        "is_active": organization.is_active,
        "created_at": organization.created_at
    }


@router.post("/deactivate-organization/{organization_id}")
async def deactivate_organization(organization_id: int,
                                  status: bool = Form(...)):
    organization = await Organization.get_or_none(id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    organization.is_active = status
    await organization.save()
    if status:
        return {"message": f"Organization {organization.name} activated successfully"}
    return {"message": f"Organization {organization.name} deactivated successfully"}


@router.put("/update-organization/{organization_id}")
async def update_organization(
    organization_id: int,
    name: str = Form(None),
):
    organization = await Organization.get_or_none(id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    if name is not None:
        organization.name = name

    await organization.save()
    return {
        "id": organization.id,
        "name": organization.name,
        "is_active": organization.is_active,
        "created_at": organization.created_at
    }



@router.delete("/delete-organization/{organization_id}")
async def delete_organization(organization_id: int):
    organization = await Organization.get_or_none(id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    await organization.delete()
    return {"message": f"Organization {organization.name} deleted successfully"}


@router.get("/")
async def list_organizations():
    organizations = await Organization.all()
    return [
        {
            "id": org.id,
            "name": org.name,
            "is_active": org.is_active,
            "created_at": org.created_at
        }
        for org in organizations
    ]



@router.get("/{organization_id}/subscription")
async def get_organization_subscription(organization_id: int):
    organization = await Organization.get_or_none(id=organization_id).prefetch_related("subscriptions")
    print(organization)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    subscription = await Subscription.get_or_none(organization=organization).prefetch_related("plan")
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found for this organization")
    return {
        "id": subscription.id,
        "plan_name": subscription.plan.name,
        "start_date": subscription.start_date,
        "end_date": subscription.end_date,
        "status": subscription.status
    }
