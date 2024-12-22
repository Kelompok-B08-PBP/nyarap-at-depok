document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const elements = {
        modal: document.getElementById('crudModal'),
        addButton: document.getElementById('addReviewBtn'),
        cancelButton: document.getElementById('cancelReview'),
        saveButton: document.getElementById('saveReview'),
        reviewForm: document.getElementById('reviewForm'),
        reviewsContainer: document.getElementById('reviewsContainer'),
        stars: document.querySelectorAll('#starRating .star'),
        ratingInput: document.getElementById('rating')
    };

    // Configuration
    const config = {
        csrfToken: document.querySelector('meta[name="csrf-token"]')?.getAttribute('content'),
        addReviewUrl: elements.addButton?.getAttribute('data-add-url')
    };

    // Review Card Generator
    const ReviewCardGenerator = {
        createStarRating(rating) {
            return Array.from({ length: 5 }, (_, i) => i < rating ? '★' : '☆')
                .map(star => `<span class="star ${star === '★' ? 'text-yellow-400' : 'text-gray-300'}">${star}</span>`)
                .join('');
        },

        generateCard(review) {
            const isProductDetailsPage = document.body.classList.contains('product-details-page');
            
            if (isProductDetailsPage) {
                return `
                    <div class="review-card bg-white rounded-lg shadow-md p-6 mb-4">
                        <div class="review-header flex justify-between items-center mb-2">
                            <div class="reviewer text-xl font-semibold">${review.restaurant_name}</div>
                            <div class="review-date text-gray-500 text-sm">${review.date_added}</div>
                        </div>
                        <p class="text-gray-600 mb-2 font-medium">Food: ${review.food_name}</p>
                        <div class="review-rating flex space-x-1 mb-2">
                            ${this.createStarRating(review.rating)}
                        </div>
                        <div class="review-text text-gray-700 mb-4">${review.review}</div>
                        <div class="flex space-x-2 mt-4">
                            <a href="/review/edit-product-review/${review.id}/" 
                               class="bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600 transition-colors">
                                Edit
                            </a>
                            <form action="/review/delete/${review.id}/" method="post" class="delete-review-form">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${config.csrfToken}">
                                <button type="submit" class="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors">
                                    Delete
                                </button>
                            </form>
                        </div>
                    </div>
                `;
            } else {
                return `
                    <div class="bg-white rounded-lg shadow-md p-6 mb-4">
                        <h3 class="text-xl font-bold mb-2">${review.restaurant_name}</h3>
                        <p class="text-gray-600 mb-2">${review.food_name}</p>
                        <div class="flex space-x-1 mb-2">
                            ${this.createStarRating(review.rating)}
                        </div>
                        <p class="text-gray-700 mb-2">${review.review}</p>
                        <p class="text-sm text-gray-500">Added on ${review.date_added}</p>
                        <div class="flex space-x-2 mt-4">
                            <a href="/review/edit-product-review/${review.id}/" 
                               class="bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600 transition-colors">
                                Edit
                            </a>
                            <form action="/review/delete/${review.id}/" method="post" class="delete-review-form">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${config.csrfToken}">
                                <button type="submit" class="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors">
                                    Delete
                                </button>
                            </form>
                        </div>
                    </div>
                `;
            }
        }
    };

    // Modal Controller
    const ModalController = {
        show() {
            elements.modal.classList.remove('hidden');
        },
        
        hide() {
            elements.modal.classList.add('hidden');
            elements.reviewForm?.reset();
            StarRatingController.reset();
        },
        
        init() {
            if (elements.addButton) elements.addButton.addEventListener('click', this.show.bind(this));
            if (elements.cancelButton) elements.cancelButton.addEventListener('click', this.hide.bind(this));
        }
    };

    // Star Rating Controller
    const StarRatingController = {
        updateStars(selectedValue) {
            elements.stars.forEach(star => {
                const value = parseInt(star.dataset.value);
                star.classList.toggle('text-yellow-400', value <= selectedValue);
                star.classList.toggle('text-gray-300', value > selectedValue);
            });
        },

        reset() {
            elements.stars.forEach(star => {
                star.classList.remove('text-yellow-400');
                star.classList.add('text-gray-300');
            });
            if (elements.ratingInput) elements.ratingInput.value = '';
        },

        init() {
            if (elements.stars.length > 0) {
                elements.stars.forEach(star => {
                    star.addEventListener('click', () => {
                        const value = parseInt(star.dataset.value);
                        if (elements.ratingInput) elements.ratingInput.value = value;
                        this.updateStars(value);
                    });
                });
            }
        }
    };

    // Review Submission Controller
    const ReviewSubmissionController = {
        async submitReview(event) {
            event.preventDefault();
            
            try {
                const formData = new FormData(elements.reviewForm);
                
                const response = await fetch(config.addReviewUrl, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': config.csrfToken,
                    },
                    body: formData
                });

                const responseData = await response.json();
                console.log('Server response:', responseData);

                if (!response.ok) {
                    throw new Error(responseData.message || 'Failed to add review');
                }

                if (elements.reviewsContainer) {
                    const noReviews = elements.reviewsContainer.querySelector('.no-reviews-placeholder');
                    if (noReviews) {
                        noReviews.remove();
                    }

                    const reviewData = responseData.data || responseData;
                    const newCardHtml = ReviewCardGenerator.generateCard(reviewData);
                    
                    const tempContainer = document.createElement('div');
                    tempContainer.innerHTML = newCardHtml;
                    elements.reviewsContainer.insertBefore(
                        tempContainer.firstElementChild, 
                        elements.reviewsContainer.firstChild
                    );
                }

                ModalController.hide();
                alert('Review added successfully!');
                
            } catch (error) {
                console.error('Error submitting review:', error);
                alert(`Error adding review: ${error.message}`);
            }
        },

        init() {
            if (elements.saveButton && elements.reviewForm) {
                elements.saveButton.addEventListener('click', this.submitReview.bind(this));
            }

            // Event delegation untuk delete forms
            if (elements.reviewsContainer) {
                elements.reviewsContainer.addEventListener('submit', async function(e) {
                    if (e.target.classList.contains('delete-review-form')) {
                        e.preventDefault();
                        
                        if (confirm('Are you sure you want to delete this review?')) {
                            const form = e.target;
                            try {
                                const response = await fetch(form.action, {
                                    method: 'POST',
                                    headers: {
                                        'X-CSRFToken': config.csrfToken,
                                    }
                                });

                                const data = await response.json();
                                
                                if (response.ok && data.status === 'success') {
                                    const reviewCard = form.closest('.bg-white');
                                    if (reviewCard) {
                                        reviewCard.style.opacity = '0';
                                        reviewCard.style.transition = 'opacity 0.3s ease';
                                        
                                        setTimeout(() => {
                                            reviewCard.remove();
                                            
                                            const remainingCards = elements.reviewsContainer.querySelectorAll('.bg-white');
                                            if (remainingCards.length === 0) {
                                                elements.reviewsContainer.innerHTML = 
                                                    '<p class="text-center text-gray-500 mt-4">No reviews yet.</p>';
                                            }
                                        }, 300);
                                    }
                                } else {
                                    throw new Error(data.message || 'Failed to delete review');
                                }
                            } catch (error) {
                                console.error('Error:', error);
                                alert('Error deleting review: ' + error.message);
                            }
                        }
                    }
                });
            }
        }
    };

    // Initialize all controllers
    if (elements.modal && elements.addButton) ModalController.init();
    if (elements.stars.length > 0) StarRatingController.init();
    if (elements.reviewForm && config.addReviewUrl) ReviewSubmissionController.init();
});