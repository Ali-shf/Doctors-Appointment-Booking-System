from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .models import Cart


def _json_error(msg, status=400):
    return JsonResponse({"error": msg}, status=status)


@require_POST
@login_required
def wallet_top_up(request):
    amount = request.POST.get("amount")
    if amount is None:
        return _json_error("amount is required")
    wallet = request.user.wallet
    try:
        new_balance = wallet.top_up(amount)
    except ValueError as e:
        return _json_error(str(e))
    return JsonResponse(
        {
            "message": "wallet topped up successfully",
            "wallet_id": wallet.id,
            "amount": str(amount),
            "balance": str(new_balance),
            "timestamp": timezone.now().isoformat(),
        }
    )


@require_POST
@login_required
def wallet_deduct(request):
    amount = request.POST.get("amount")
    if amount is None:
        return _json_error("amount is required")

    cart_id = request.POST.get("cart_id")
    cart = None
    if cart_id:
        try:
            cart = Cart.objects.get(pk=cart_id)
        except Cart.DoesNotExist:
            return _json_error("cart not found", status=404)

    wallet = request.user.wallet
    try:
        new_balance = wallet.deduct(amount, cart=cart)
    except ValueError as e:
        return _json_error(str(e))
    return JsonResponse(
        {
            "message": "wallet deducted successfully",
            "wallet_id": wallet.id,
            "amount": str(amount),
            "balance": str(new_balance),
            "cart_id": cart.id if cart else None,
            "timestamp": timezone.now().isoformat(),
        }
    )


@require_GET
@login_required
def wallet_balance(request):
    wallet = request.user.wallet
    return JsonResponse(
        {
            "wallet_id": wallet.id,
            "code": wallet.code,
            "balance": str(wallet.balance),
            "updated_at": wallet.updated_at.isoformat(),
        }
    )


@require_GET
@login_required
def wallet_transactions(request):
    wallet = request.user.wallet
    qs = wallet.transactions.order_by("-created_at")

    tx_type = request.GET.get("type")
    if tx_type:
        qs = qs.filter(payment_type__iexact=tx_type)

    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1
    try:
        page_size = int(request.GET.get("page_size", 20))
    except ValueError:
        page_size = 20
    page_size = max(1, min(page_size, 100))

    paginator = Paginator(qs, page_size)
    page_obj = paginator.get_page(page)

    results = [
        {
            "id": tx.id,
            "payment_type": tx.payment_type,
            "amount": str(tx.amount),
            "cart_id": tx.cart_id,
            "created_at": tx.created_at.isoformat(),
        }
        for tx in page_obj.object_list
    ]

    return JsonResponse(
        {
            "wallet_id": wallet.id,
            "count": paginator.count,
            "num_pages": paginator.num_pages,
            "page": page_obj.number,
            "results": results,
        }
    )