-- CivicQ Database Views
--
-- Materialized and regular views for common queries.
-- These improve performance for frequently-accessed data.

-- ============================================================================
-- Popular Questions View
-- ============================================================================

CREATE OR REPLACE VIEW popular_questions AS
SELECT
    q.id,
    q.contest_id,
    q.question_text,
    q.rank_score,
    q.status,
    q.issue_tags,
    q.created_at,
    COUNT(v.id) as vote_count,
    SUM(CASE WHEN v.value = 1 THEN 1 ELSE 0 END) as upvote_count,
    SUM(CASE WHEN v.value = -1 THEN 1 ELSE 0 END) as downvote_count,
    u.full_name as author_name,
    u.id as author_id,
    c.title as contest_title,
    c.type as contest_type
FROM questions q
LEFT JOIN votes v ON v.question_id = q.id
LEFT JOIN users u ON u.id = q.author_id
LEFT JOIN contests c ON c.id = q.contest_id
WHERE q.status = 'approved'
GROUP BY q.id, u.full_name, u.id, c.title, c.type
ORDER BY q.rank_score DESC;

-- ============================================================================
-- Contest Summary View
-- ============================================================================

CREATE OR REPLACE VIEW contest_summary AS
SELECT
    c.id,
    c.ballot_id,
    c.title,
    c.type,
    c.office,
    c.display_order,
    b.city_id,
    b.city_name,
    b.election_date,
    COUNT(DISTINCT CASE WHEN c.type = 'race' THEN cand.id END) as candidate_count,
    COUNT(DISTINCT q.id) as question_count,
    COUNT(DISTINCT CASE WHEN q.status = 'approved' THEN q.id END) as approved_question_count,
    COUNT(DISTINCT va.id) as video_answer_count,
    MAX(q.created_at) as latest_question_at,
    MAX(va.created_at) as latest_answer_at
FROM contests c
JOIN ballots b ON b.id = c.ballot_id
LEFT JOIN candidates cand ON cand.contest_id = c.id AND cand.status = 'active'
LEFT JOIN questions q ON q.contest_id = c.id
LEFT JOIN video_answers va ON va.question_id = q.id AND va.status = 'published'
GROUP BY c.id, b.city_id, b.city_name, b.election_date
ORDER BY b.election_date, c.display_order;

-- ============================================================================
-- Candidate Profile View
-- ============================================================================

CREATE OR REPLACE VIEW candidate_profiles AS
SELECT
    cand.id,
    cand.name,
    cand.status,
    cand.photo_url,
    cand.website,
    cand.contest_id,
    c.title as contest_title,
    c.office,
    b.city_id,
    b.city_name,
    b.election_date,
    u.id as user_id,
    u.email as user_email,
    COUNT(DISTINCT va.id) as answer_count,
    COUNT(DISTINCT CASE WHEN va.status = 'published' THEN va.id END) as published_answer_count,
    COUNT(DISTINCT r.id) as rebuttal_count,
    AVG(CASE WHEN va.duration IS NOT NULL THEN va.duration END) as avg_answer_duration,
    MAX(va.created_at) as latest_answer_at
FROM candidates cand
JOIN contests c ON c.id = cand.contest_id
JOIN ballots b ON b.id = c.ballot_id
LEFT JOIN users u ON u.id = cand.user_id
LEFT JOIN video_answers va ON va.candidate_id = cand.id
LEFT JOIN rebuttals r ON r.candidate_id = cand.id
GROUP BY cand.id, c.title, c.office, b.city_id, b.city_name, b.election_date, u.id, u.email
ORDER BY cand.display_order;

-- ============================================================================
-- User Activity Summary View
-- ============================================================================

CREATE OR REPLACE VIEW user_activity_summary AS
SELECT
    u.id,
    u.email,
    u.full_name,
    u.role,
    u.city_id,
    u.verification_status,
    u.created_at,
    u.last_active,
    COUNT(DISTINCT q.id) as questions_submitted,
    COUNT(DISTINCT v.id) as votes_cast,
    COUNT(DISTINCT f.id) as follows_count,
    COUNT(DISTINCT r.id) as reports_filed,
    MAX(q.created_at) as latest_question_at,
    MAX(v.created_at) as latest_vote_at
FROM users u
LEFT JOIN questions q ON q.author_id = u.id
LEFT JOIN votes v ON v.user_id = u.id
LEFT JOIN follows f ON f.user_id = u.id AND f.is_active = true
LEFT JOIN reports r ON r.reporter_id = u.id
GROUP BY u.id
ORDER BY u.last_active DESC;

-- ============================================================================
-- Video Answer Stats View
-- ============================================================================

CREATE OR REPLACE VIEW video_answer_stats AS
SELECT
    va.id,
    va.question_id,
    va.candidate_id,
    va.status,
    va.duration,
    va.created_at,
    q.question_text,
    q.contest_id,
    cand.name as candidate_name,
    c.title as contest_title,
    COUNT(DISTINCT cl.id) as claim_count,
    COUNT(DISTINCT CASE WHEN cl.is_verified = true THEN cl.id END) as verified_claim_count,
    COUNT(DISTINCT r.id) as rebuttal_count,
    v.view_count,
    v.watch_time_seconds,
    CASE
        WHEN v.watch_time_seconds > 0 AND va.duration > 0
        THEN (v.watch_time_seconds::float / (va.duration * v.view_count)) * 100
        ELSE 0
    END as avg_completion_percent
FROM video_answers va
JOIN questions q ON q.id = va.question_id
JOIN candidates cand ON cand.id = va.candidate_id
JOIN contests c ON c.id = q.contest_id
LEFT JOIN claims cl ON cl.answer_id = va.id
LEFT JOIN rebuttals r ON r.target_answer_id = va.id
LEFT JOIN videos v ON v.answer_id = va.id
GROUP BY va.id, q.question_text, q.contest_id, cand.name, c.title, v.view_count, v.watch_time_seconds
ORDER BY va.created_at DESC;

-- ============================================================================
-- City Dashboard View
-- ============================================================================

CREATE OR REPLACE VIEW city_dashboard AS
SELECT
    city.id,
    city.name,
    city.slug,
    city.state,
    city.status,
    city.population,
    city.next_election_date,
    city.created_at,
    COUNT(DISTINCT u.id) as total_users,
    COUNT(DISTINCT CASE WHEN u.verification_status = 'verified' THEN u.id END) as verified_users,
    COUNT(DISTINCT CASE WHEN u.role = 'voter' THEN u.id END) as voter_count,
    COUNT(DISTINCT CASE WHEN u.role = 'candidate' THEN u.id END) as candidate_count,
    COUNT(DISTINCT b.id) as ballot_count,
    COUNT(DISTINCT c.id) as contest_count,
    COUNT(DISTINCT q.id) as question_count,
    COUNT(DISTINCT CASE WHEN q.status = 'approved' THEN q.id END) as approved_question_count,
    COUNT(DISTINCT v.id) as total_votes,
    COUNT(DISTINCT cs.id) as staff_count,
    MAX(u.created_at) as latest_user_signup,
    MAX(q.created_at) as latest_question_at
FROM cities city
LEFT JOIN users u ON u.city_id = city.slug
LEFT JOIN ballots b ON b.city_id = city.slug
LEFT JOIN contests c ON c.ballot_id = b.id
LEFT JOIN questions q ON q.contest_id = c.id
LEFT JOIN votes v ON v.question_id = q.id
LEFT JOIN city_staff cs ON cs.city_id = city.id AND cs.is_active = true
GROUP BY city.id
ORDER BY city.name;

-- ============================================================================
-- Moderation Queue View
-- ============================================================================

CREATE OR REPLACE VIEW moderation_queue AS
SELECT
    'question' as item_type,
    q.id as item_id,
    q.question_text as content_preview,
    q.created_at,
    q.is_flagged as flag_count,
    u.full_name as author_name,
    u.id as author_id,
    c.title as contest_title,
    COUNT(DISTINCT r.id) as report_count,
    MAX(r.created_at) as latest_report_at
FROM questions q
JOIN users u ON u.id = q.author_id
JOIN contests c ON c.id = q.contest_id
LEFT JOIN reports r ON r.target_type = 'question' AND r.target_id = q.id AND r.status = 'pending'
WHERE q.status = 'pending' OR q.is_flagged > 0
GROUP BY q.id, u.full_name, u.id, c.title

UNION ALL

SELECT
    'report' as item_type,
    r.id as item_id,
    r.description as content_preview,
    r.created_at,
    0 as flag_count,
    u.full_name as author_name,
    u.id as author_id,
    r.target_type as contest_title,
    1 as report_count,
    r.created_at as latest_report_at
FROM reports r
JOIN users u ON u.id = r.reporter_id
WHERE r.status = 'pending'

ORDER BY latest_report_at DESC;

-- ============================================================================
-- Trending Questions View (24 hours)
-- ============================================================================

CREATE OR REPLACE VIEW trending_questions AS
SELECT
    q.id,
    q.contest_id,
    q.question_text,
    q.rank_score,
    q.created_at,
    c.title as contest_title,
    u.full_name as author_name,
    COUNT(v.id) as recent_votes,
    SUM(CASE WHEN v.value = 1 THEN 1 ELSE 0 END) as recent_upvotes,
    SUM(CASE WHEN v.value = -1 THEN 1 ELSE 0 END) as recent_downvotes
FROM questions q
JOIN contests c ON c.id = q.contest_id
LEFT JOIN users u ON u.id = q.author_id
LEFT JOIN votes v ON v.question_id = q.id AND v.created_at > NOW() - INTERVAL '24 hours'
WHERE q.status = 'approved'
GROUP BY q.id, c.title, u.full_name
HAVING COUNT(v.id) > 0
ORDER BY recent_votes DESC, q.rank_score DESC
LIMIT 100;

-- ============================================================================
-- Audit Trail View (last 7 days)
-- ============================================================================

CREATE OR REPLACE VIEW recent_audit_trail AS
SELECT
    al.id,
    al.event_type,
    al.created_at,
    al.severity,
    al.city_scope,
    u.full_name as actor_name,
    u.email as actor_email,
    u.role as actor_role,
    al.target_type,
    al.target_id,
    al.event_data
FROM audit_logs al
LEFT JOIN users u ON u.id = al.actor_id
WHERE al.created_at > NOW() - INTERVAL '7 days'
ORDER BY al.created_at DESC;

-- ============================================================================
-- Indexes for Views
-- ============================================================================

-- Note: Some views may benefit from materialized views for better performance
-- Example of creating a materialized view:
--
-- CREATE MATERIALIZED VIEW mv_city_dashboard AS
-- SELECT * FROM city_dashboard;
--
-- CREATE UNIQUE INDEX ON mv_city_dashboard(id);
--
-- Refresh with:
-- REFRESH MATERIALIZED VIEW mv_city_dashboard;

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Function to refresh all materialized views
CREATE OR REPLACE FUNCTION refresh_all_materialized_views()
RETURNS void AS $$
DECLARE
    view_name text;
BEGIN
    FOR view_name IN
        SELECT matviewname
        FROM pg_matviews
        WHERE schemaname = 'public'
    LOOP
        EXECUTE 'REFRESH MATERIALIZED VIEW ' || view_name;
        RAISE NOTICE 'Refreshed materialized view: %', view_name;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Usage: SELECT refresh_all_materialized_views();
