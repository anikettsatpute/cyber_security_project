# Intents

## track_order

- give_order_id
  - Entity: order_id

## cancel_order

- give_order_id
  - Entity: order_id
- give_reason
  - Entity: reason

## product_search

- give_product_name
  - Entity: product_name
- give_product_category
  - Entity: product_category
- give_product_brand
  - Entity: brand_name
- give_product_price
  - Entity: price
  - Entity: lower_bound
  - Entity: upper_bound
- give_product_rating
  - Entity: rating
- give_product_features
  - Entity: features

## change_order

- give_order_id
  - Entity: order_id
- give_change
  - Entity: change
- give_reason
  - Entity: reason
- Entity: item_to_be_removed

## change_address

- give_order_id
  - Entity: order_id
- give_new_address
  - Entity: address

## get_invoice

- give_order_id
  - Entity: order_id

## complaint

- give_order_id
  - Entity: order_id
- give_complaint
  - Entity: complaint
- give_item
  - Entity: item

## refund_status

- give_order_id
  - Entity: order_id

## review

- give_order_id
  - Entity: order_id
- give_rating
  - Entity: rating
- give_review
  - Entity: review
- give_item
  - Entity: item

## contact_human

- give_reason
  - Entity: reason
