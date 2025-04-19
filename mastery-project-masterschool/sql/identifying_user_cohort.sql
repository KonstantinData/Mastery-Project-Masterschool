/*
This SQL query identifies active users who have had at least 7 valid (non-cancelled) sessions since January 4th, 2023.
It then retrieves detailed session data for those users by joining related information from users, flights, and hotels.
*/

-- Step 1: Identify users with at least 7 valid sessions after January 4, 2023

WITH active_users AS (
  SELECT user_id
  FROM sessions
  WHERE session_start > '2023-01-04'
    AND cancellation = FALSE
  GROUP BY user_id
  HAVING COUNT(session_id) >= 7
)

-- Step 2: Retrieve session details for those active users
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
  htl.hotel_per_room_usd
FROM sessions AS ses
-- Optional join with users table (not used in select)
LEFT JOIN users AS usr ON ses.user_id = usr.user_id
-- Get flight-related info based on trip_id
LEFT JOIN flights AS fli ON ses.trip_id = fli.trip_id
-- Get hotel-related info based on trip_id
LEFT JOIN hotels AS htl ON ses.trip_id = htl.trip_id
-- Join with active users to filter only sessions from those users
JOIN active_users AS au ON ses.user_id = au.user_id
-- Ensure we only include sessions that are valid and after the cutoff date
WHERE ses.session_start > '2023-01-04'
  AND ses.cancellation = FALSE;


-- 🧠 Quick Summary:

-- Filters sessions after Jan 4, 2023

-- Excludes cancelled sessions

-- Identifies users with at least 7 sessions

-- Joins in relevant trip data (flight & hotel)

-- Output is one row per session, including perks and activity data
