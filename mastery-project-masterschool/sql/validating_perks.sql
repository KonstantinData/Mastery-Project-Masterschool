/*
---------------------------------------------------------------------------------
SQL Query: Validating Perks for Active Users Based on Session Data
---------------------------------------------------------------------------------

Description:
This query identifies and analyzes active users who have had at least 7 valid
(non-cancelled) sessions after January 4th, 2023. It retrieves session-level data
from the sessions table, enriching it with trip-related information via joins
to the flights and hotels tables.

For each session, the query flags the presence of the following perks:

1. Free checked bag                 → User had at least one checked bag
2. No cancellation fees            → Session was not cancelled
3. Exclusive discounts             → Flight or hotel discount was applied
4. One night free hotel with flight→ Hotel was booked for one night alongside
                                      a flight and was either fully discounted
                                      or free of charge

Only perks supported by the dataset are included. These indicators help
understand perk usage and engagement at the session level.
*/

-- Step 1: Find users with at least 7 valid sessions after January 4, 2023
WITH active_users AS (
  SELECT user_id
  FROM sessions
  WHERE session_start > '2023-01-04'
    AND cancellation = FALSE
  GROUP BY user_id
  HAVING COUNT(session_id) >= 7
)

-- Step 2: Return detailed session data including perk flags
SELECT
  ses.user_id,
  ses.session_id,
  ses.trip_id,
  ses.flight_discount,
  ses.hotel_discount,
  ses.flight_discount_amount,
  ses.hotel_discount_amount,
  ses.flight_booked,
  ses.hotel_booked,
  ses.page_clicks,
  ses.cancellation,
  fli.checked_bags,
  fli.base_fare_usd,
  htl.nights,
  htl.hotel_per_room_usd,

  -- Perk 1: Free checked bag
  CASE
    WHEN fli.checked_bags >= 1 THEN TRUE
    ELSE FALSE
  END AS perk_free_checked_bag,

  -- Perk 2: No cancellation fees
  CASE
    WHEN ses.cancellation = FALSE THEN TRUE
    ELSE FALSE
  END AS perk_no_cancellation_fees,

  -- Perk 3: Exclusive discounts
  CASE
    WHEN ses.flight_discount = TRUE OR ses.hotel_discount = TRUE THEN TRUE
    ELSE FALSE
  END AS perk_exclusive_discount,

  -- Perk 4: One night free hotel with flight
  CASE
    WHEN ses.flight_booked = TRUE
         AND ses.hotel_booked = TRUE
         AND htl.nights = 1
         AND (
              htl.hotel_per_room_usd = 0
              OR ses.hotel_discount_amount = htl.hotel_per_room_usd
         )
    THEN TRUE
    ELSE FALSE
  END AS perk_one_night_free_hotel_with_flight

FROM sessions AS ses
LEFT JOIN users AS usr ON ses.user_id = usr.user_id
LEFT JOIN flights AS fli ON ses.trip_id = fli.trip_id
LEFT JOIN hotels AS htl ON ses.trip_id = htl.trip_id
JOIN active_users AS au ON ses.user_id = au.user_id
WHERE ses.session_start > '2023-01-04'
  AND ses.cancellation = FALSE;
