from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File, Query
from applications.subscription.models import Plan, Subscription, SubscriptionStatus
from applications.organization.models import Organization
from datetime import date, timedelta



router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])



@router.post("/create-plan")
async def create_plan(
    name: str = Form(...),
    price: float = Form(...),
    duration_days: int = Form(...),
):

    plan = await Plan.create(
        name=name,
        price=price,
        duration_days=duration_days
    )
    return {"id": plan.id, "name": plan.name, "price": f"{plan.price:.2f}", "duration_days": plan.duration_days}




@router.get("/plans")
async def list_plans(
    active: bool = Query(None, description="Filter by active status")
):
    query = Plan.all()
    if active is not None:
        query = query.filter(is_active=active)
    plans = await query
    return [
        {"id": plan.id, "name": plan.name, "price": f"{plan.price:.2f}", "duration_days": plan.duration_days, "is_active": plan.is_active}
        for plan in plans
    ]

@router.post("/deactivate-plan/{plan_id}")
async def deactivate_plan(plan_id: int,
                          status: bool = Form(...)):
    plan = await Plan.get_or_none(id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    plan.is_active = status
    await plan.save()
    if status:
        return {"message": f"Plan {plan.name} activated successfully"}
    return {"message": f"Plan {plan.name} deactivated successfully"}

@router.get("/plan/{plan_id}")
async def get_plan(plan_id: int):
    plan = await Plan.get_or_none(id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"id": plan.id, "name": plan.name, "price": f"{plan.price:.2f}", "duration_days": plan.duration_days, "is_active": plan.is_active}


@router.put("/update-plan/{plan_id}")
async def update_plan(
    plan_id: int,
    name: str = Form(None),
    price: float = Form(None),
    duration_days: int = Form(None),
):
    plan = await Plan.get_or_none(id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if name is not None:
        plan.name = name
    if price is not None:
        plan.price = price
    if duration_days is not None:
        plan.duration_days = duration_days

    await plan.save()
    return {"id": plan.id, "name": plan.name, "price": f"{plan.price:.2f}", "duration_days": plan.duration_days}

@router.delete("/delete-plan/{plan_id}")
async def delete_plan(plan_id: int):
    plan = await Plan.get_or_none(id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    await plan.delete()
    return {"message": f"Plan {plan.name} deleted successfully"}




#===============================================================================
# Subscription Endpoints
#===============================================================================


@router.post("/subscribe/{plan_id}")
async def subscribe_to_plan(
    plan_id: int,
    organization_id: int = Form(...),
):
    plan = await Plan.get_or_none(id=plan_id, is_active=True)
    if not plan:
        raise HTTPException(status_code=404, detail="Active plan not found")
    organization = await Organization.get_or_none(id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    start_date = date.today()
    end_date = start_date + timedelta(days=plan.duration_days)

    subscription = await Subscription.create(
        plan=plan,
        organization=organization,
        start_date=start_date,
        end_date=end_date,
        status=SubscriptionStatus.ACTIVE
    )
    return {"message": "Subscription created successfully", "subscription_id": subscription.id}


@router.get("/subscriptions")
async def list_subscriptions(
    status: SubscriptionStatus = Query(None, description="Filter by subscription status")
):
    query = Subscription.all().prefetch_related("plan", "organization")
    if status is not None:
        query = query.filter(status=status)
    subscriptions = await query
    return [
        {
            "id": sub.id,
            "organization": sub.organization.name,
            "plan": sub.plan.name,
            "start_date": sub.start_date,
            "end_date": sub.end_date,
            "status": sub.status,
            "auto_renew": sub.auto_renew
        }
        for sub in subscriptions
    ]


@router.put("/update-subscription/{subscription_id}")
async def update_subscription(
    subscription_id: int,
    auto_renew: bool = Form(None),
):
    subscription = await Subscription.get_or_none(id=subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if auto_renew is not None:
        subscription.auto_renew = auto_renew

    await subscription.save()
    return {
        "id": subscription.id,
        "organization_id": subscription.organization_id,
        "plan_id": subscription.plan_id,
        "start_date": subscription.start_date,
        "end_date": subscription.end_date,
        "status": subscription.status,
        "auto_renew": subscription.auto_renew
    }

@router.delete("/delete-subscription/{subscription_id}")
async def delete_subscription(subscription_id: int):    
    subscription = await Subscription.get_or_none(id=subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    await subscription.delete()
    return {"message": f"Subscription {subscription.id} deleted successfully"}


@router.get("/subscription/{subscription_id}")
async def get_subscription(subscription_id: int):
    subscription = await Subscription.get_or_none(id=subscription_id).prefetch_related("plan", "organization")
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {
        "id": subscription.id,
        "organization": subscription.organization.name,
        "plan": subscription.plan.name,
        "start_date": subscription.start_date,
        "end_date": subscription.end_date,
        "status": subscription.status,
        "auto_renew": subscription.auto_renew
    }



    
