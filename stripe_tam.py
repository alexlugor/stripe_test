# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys

import stripe

stripe.api_key = "{{TEST_SECRET_KEY}}"

# Plan A: Flat-rate $24.99/month for unlimited usage

# Create Product for the Unlimited Usage plan
product = stripe.Product.create(name="Unlimited Usage")

# Create a price for the Unlimited Usage plan product
price = stripe.Price.create(
  unit_amount = 2499, # Amount in cents
  currency = "usd",
  recurring = {"interval": "month"},
  product = product.id,
)

# Specify customer and price when creating the subscription
subscription = stripe.Subscription.create(
  customer = "cus_xxxxxxxxxxxxx", # Replace with the actual customer Id
  items = [{"price": price.id}],
)


# Plan B: $10.99 for first 100 GB, then $1 per 10 GB
meter = stripe.billing.Meter.create(
  display_name="Usage-based Plan",
  event_name="blocks_of_10",
  default_aggregation={"formula": "sum"},
  customer_mapping={"event_payload_key": "stripe_customer_id", "type": "by_id"},
  value_settings={"event_payload_key": "value"},
)

# Create flat fee price of $10.99 for the first 100 GB
product_usage = stripe.Product.create(name="Usage-Based Plan")

# Create price for the first 100 GB
price_flat = stripe.Price.create(
  product= product_usage.id,
  currency="usd",
  unit_amount=1099,
  billing_scheme="per_unit",
  recurring={"usage_type": "licensed", "interval": "month"},
)

# Create metered price.
# First tier, specify 0 to 1 unit at 10.99. For second tier specify $ 0.10 per unit
price_metered = stripe.Price.create(
  product = product.id,
  currency = "usd",
  billing_scheme = "tiered",
  recurring = {"usage_type": "metered", "interval": "month", "meter": meter.id},
  tiers_mode = "volume",
  tiers=[
    {"up_to": 1, "unit_amount_decimal": "0"},
    {"up_to": "inf", "unit_amount_decimal": "1"},
  ],
)

#Finally, specify both price IDs when creating a subscription
subscription_usage_based_plan = stripe.Subscription.create(
  customer="cus_xxxxxxxxxxxxx",
  items=[
    {"price": price_flat.id, "quantity": 1},
    {"price": price_metered.id}
    ],

)

# Add a coupon (e.g., 20% off one-time)
coupon = stripe.Coupon.create(
  percent_off=20,
  duration=" once"
)

# Apply the coupon to a subscription
subscription_with_coupon = stripe.Subscription.create(
  customer="cus_xxxxxxxxxxxxx",
  items=[{"price": "price_xxxxxxxxxxxxx"}],
  coupon = coupon.id
)
