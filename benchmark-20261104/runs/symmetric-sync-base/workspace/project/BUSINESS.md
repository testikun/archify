# Shared status synchronization

Project Management and ERP synchronize the same project status with one another. Either system can initiate a status update and both directions have the same meaning. Treat this as one symmetric synchronization relationship, not two differently named messages. Each system also sends an audit summary to Audit Storage. Audit Storage does not send updates back. No protocol, retry mechanism or timing information is established.
