-- SELECT COUNT(evaluations.outstanding) AS outstandings, teams.intra_id, teams.best, teams.current
-- FROM evaluations
-- JOIN teams ON teams.intra_id = evaluations.intra_team_id
-- WHERE evaluations.outstanding = 't'
-- GROUP BY teams.intra_id, teams.best, teams.current
-- ORDER BY teams.intra_id;

-- SELECT COUNT(CASE WHEN outstanding THEN 1 END) AS outstandings, teams.intra_id, teams.best, teams.current, teams.projects_user_id
-- FROM teams
-- JOIN evaluations ON teams.intra_id = evaluations.intra_team_id
-- WHERE teams.user_id = 76647
-- GROUP BY teams.intra_id
-- ORDER BY teams.projects_user_id;

-- SELECT COUNT(CASE WHEN outstanding THEN 1 END) AS outstandings, teams.intra_id, teams.best, teams.current, teams.projects_user_id
-- FROM teams, evaluations
-- WHERE teams.user_id = 76647
-- GROUP BY teams.intra_id
-- ORDER BY teams.projects_user_id;

-- SELECT DISTINCT a.intra_id, MIN(a.projects_user_id)
-- FROM teams a
-- JOIN teams b ON a.intra_id = b.intra_id
-- JOIN evaluations ON a.intra_id = evaluations.intra_team_id
-- WHERE a.user_id = 76647
-- GROUP BY a.intra_id;
