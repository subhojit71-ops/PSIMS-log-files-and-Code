SELECT 
    d.UIN,
    d.full_name,
    d.specialty,
    COUNT(DISTINCT e.UIN) as event_count,
    COUNT(DISTINCT ct.UIN) as trial_count,
    COUNT(DISTINCT pm.UIN) as press_count,
    d.area_of_interest
FROM doctors d
LEFT JOIN events e ON d.UIN = e.UIN
LEFT JOIN clinical_trials ct ON d.UIN = ct.UIN
LEFT JOIN press_mentions pm ON d.UIN = pm.UIN
WHERE d.area_of_interest LIKE '%patient%' 
   OR d.area_of_interest LIKE '%care%'
   OR d.area_of_interest LIKE '%community%'
GROUP BY d.UIN, d.full_name, d.specialty, d.area_of_interest
HAVING (event_count + trial_count + press_count) > 0
ORDER BY (event_count + trial_count + press_count) DESC
LIMIT 10;