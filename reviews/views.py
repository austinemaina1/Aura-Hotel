from django.shortcuts import render, redirect, get_object_or_404
from .models import Review


def review_list(request):

    reviews = Review.objects.all()

    return render(
        request,
        'reviews/review_list.html',
        {'reviews': reviews}
    )


def create_review(request):

    if request.method == 'POST':

        Review.objects.create(
            guest_name=request.POST.get('guest_name'),
            rating=request.POST.get('rating'),
            comment=request.POST.get('comment')
        )

        return redirect('review_list')

    return render(request, 'reviews/create_review.html')


def edit_review(request, id):

    review = get_object_or_404(
        Review,
        id=id
    )

    if request.method == 'POST':

        review.guest_name = request.POST.get('guest_name')
        review.rating = request.POST.get('rating')
        review.comment = request.POST.get('comment')

        review.save()

        return redirect('review_list')

    return render(
        request,
        'reviews/edit_review.html',
        {'review': review}
    )


def delete_review(request, id):

    review = get_object_or_404(
        Review,
        id=id
    )

    if request.method == 'POST':
        review.delete()
        return redirect('review_list')

    return render(
        request,
        'reviews/delete_review.html',
        {'review': review}
    )


from django.shortcuts import render
from django.db.models import Avg
from django.db.models.functions import TruncMonth
from .models import Review


def review_dashboard(request):

    total_reviews = Review.objects.count()

    average_rating = Review.objects.aggregate(
        Avg('rating')
    )['rating__avg'] or 0

    five_star_reviews = Review.objects.filter(
        rating=5
    ).count()

    four_star_reviews = Review.objects.filter(
        rating=4
    ).count()

    three_star_reviews = Review.objects.filter(
        rating=3
    ).count()

    two_star_reviews = Review.objects.filter(
        rating=2
    ).count()

    one_star_reviews = Review.objects.filter(
        rating=1
    ).count()

    recent_reviews = Review.objects.order_by(
        '-created_at'
    )[:5]

    monthly_reviews = (
        Review.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .order_by('month')
    )

    chart_labels = []
    chart_data = []

    for item in monthly_reviews:
        chart_labels.append(
            item['month'].strftime('%b %Y')
        )

        count = Review.objects.filter(
            created_at__year=item['month'].year,
            created_at__month=item['month'].month
        ).count()

        chart_data.append(count)

    context = {
        'total_reviews': total_reviews,
        'average_rating': round(average_rating, 1),

        'five_star_reviews': five_star_reviews,

        'one_star_reviews': one_star_reviews,
        'two_star_reviews': two_star_reviews,
        'three_star_reviews': three_star_reviews,
        'four_star_reviews': four_star_reviews,
        'five_star_reviews': five_star_reviews,

        'recent_reviews': recent_reviews,

        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }

    return render(
        request,
        'reviews/review_dashboard.html',
        context
    )

    
