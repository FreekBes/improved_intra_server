-- The OAuth2Token model is gone. Its only reader was /testkey.php, which went
-- with the v3 extension support; nothing has read the row since. Fresh
-- installs never create the table, so this is a no-op for them.
DROP TABLE IF EXISTS oauth2_tokens;
