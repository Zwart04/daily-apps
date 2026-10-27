-- Additive migration. Existing users, sessions, records and workspace IDs remain intact.
CREATE TABLE IF NOT EXISTS workspace_areas (
 root_id TEXT NOT NULL REFERENCES workspaces(id), area TEXT NOT NULL,
 workspace_id TEXT NOT NULL UNIQUE REFERENCES workspaces(id),
 created_at INTEGER NOT NULL, PRIMARY KEY(root_id,area)
);
CREATE INDEX IF NOT EXISTS workspace_areas_root ON workspace_areas(root_id);
CREATE TABLE IF NOT EXISTS workspace_project_links (
 root_id TEXT NOT NULL REFERENCES workspaces(id), project_id TEXT NOT NULL REFERENCES records(id),
 record_id TEXT NOT NULL REFERENCES records(id), actor_id TEXT NOT NULL REFERENCES users(id),
 created_at INTEGER NOT NULL, PRIMARY KEY(project_id,record_id)
);
CREATE INDEX IF NOT EXISTS project_links_root ON workspace_project_links(root_id,project_id);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_focus ON records(workspace_id,json_extract(data,'$.user_id'))
 WHERE kind='focus_sessions' AND status='active' AND deleted_at IS NULL;
