# CivicQ Operations Documentation

**Complete deployment and operations guide for production CivicQ deployments**

Last Updated: 2026-02-14

---

## Documentation Index

### Core Operations Guides

✅ **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete deployment guide
- Prerequisites and accounts needed
- Step-by-step deployment for AWS, GCP, DigitalOcean, and VPS
- Environment configuration
- Database, Redis, S3, Email, CDN setup
- SSL certificates and domain configuration
- First-time admin setup
- Smoke testing procedures

✅ **[OPERATIONS_MANUAL.md](OPERATIONS_MANUAL.md)** - Day-to-day operations
- Daily operations checklist
- Weekly maintenance tasks
- Monthly review procedures
- Health monitoring
- Log management
- Database maintenance
- Certificate management
- Dependency updates
- Common tasks and procedures

✅ **[SCALING_GUIDE.md](SCALING_GUIDE.md)** - How to scale from 1K to 1M+ users
- When to scale (metrics and indicators)
- Vertical scaling (bigger servers)
- Horizontal scaling (more servers)
- Database scaling (replicas, partitioning)
- Redis scaling (clustering)
- Celery worker scaling
- CDN optimization
- Auto-scaling configuration
- Load balancer setup
- Cost optimization strategies

✅ **[TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md)** - Common issues and solutions
- Service won't start
- Database connection issues
- Redis connection issues
- Email delivery failures
- Video processing failures
- High error rates
- Slow performance
- Out of disk space
- Out of memory
- SSL certificate issues
- DNS/Domain issues
- Emergency recovery procedures

✅ **[BACKUP_RECOVERY.md](BACKUP_RECOVERY.md)** - Disaster recovery
- Backup schedule and retention policies
- Database backup and restoration procedures
- Redis backup procedures
- File storage backup (videos, images)
- Configuration backups
- Full system restore procedures
- Disaster recovery scenarios
- RTO/RPO targets
- Testing restore procedures

### Additional Resources

See the main [/docs](../) directory for:

- **SECURITY.md** - Security policy and best practices
- **AUTHENTICATION_GUIDE.md** - Auth system documentation
- **API_ENDPOINTS.md** - API reference
- **VIDEO_INFRASTRUCTURE.md** - Video processing system
- **CITY_ONBOARDING.md** - City admin guide
- **QUICK_START.md** - Developer quick start

---

## Quick Reference

### Emergency Contacts

- **Operations Team**: ops@civicq.org
- **On-Call Engineer**: See MONITORING_RUNBOOK.md
- **Emergency Hotline**: [TBD]
- **Security Issues**: security@civicq.org

### Quick Diagnostics

```bash
# Check all services
docker-compose ps

# View logs
docker-compose logs --tail=100 backend

# Health check
curl https://api.civicq.example.com/health

# Database status
docker-compose exec postgres psql -U civicq -c "SELECT 1;"

# Redis status
docker-compose exec redis redis-cli -a $REDIS_PASSWORD ping

# System resources
htop
df -h
free -h
```

### Common Commands

```bash
# Restart services
docker-compose restart backend
docker-compose restart nginx

# Scale services
docker-compose up -d --scale backend=4
docker-compose up -d --scale celery-worker=8

# View real-time logs
docker-compose logs -f backend

# Database backup
docker-compose exec postgres pg_dump -U civicq civicq | gzip > backup-$(date +%Y%m%d).sql.gz

# Clear cache
docker-compose exec redis redis-cli -a $REDIS_PASSWORD FLUSHDB

# Run migrations
docker-compose exec backend alembic upgrade head
```

---

## Deployment Paths

### Path 1: Quick VPS Deployment (Recommended for Small Cities)

**Time**: 2-3 hours | **Cost**: $50-100/month | **Complexity**: Low

1. Provision Ubuntu 22.04 VPS (Linode, Vultr, Hetzner)
2. Install Docker and Docker Compose
3. Clone repository
4. Configure environment variables
5. Run `docker-compose up -d`
6. Configure domain and SSL with Let's Encrypt
7. Create first admin user
8. Test deployment

**Best for**: Cities with <10,000 voters, single-server deployments

**See**: DEPLOYMENT_GUIDE.md > VPS Deployment section

### Path 2: AWS Deployment (Recommended for Medium-Large Cities)

**Time**: 4-6 hours | **Cost**: $200-500/month | **Complexity**: Medium

1. Set up AWS account and VPC
2. Create RDS PostgreSQL database
3. Create ElastiCache Redis
4. Create S3 bucket for media
5. Deploy backend with ECS or EC2
6. Configure CloudFront CDN
7. Set up Application Load Balancer
8. Configure auto-scaling

**Best for**: Cities with 10,000-100,000 voters, high availability needed

**See**: DEPLOYMENT_GUIDE.md > AWS Deployment section

### Path 3: Google Cloud Deployment

**Time**: 4-6 hours | **Cost**: $200-500/month | **Complexity**: Medium

1. Create GCP project
2. Create Cloud SQL PostgreSQL
3. Create Memorystore Redis
4. Create Cloud Storage bucket
5. Deploy with Cloud Run or GKE
6. Configure Cloud CDN
7. Set up Cloud Load Balancing

**Best for**: Cities with 10,000-100,000 voters, Google ecosystem preference

**See**: DEPLOYMENT_GUIDE.md > Google Cloud section

### Path 4: DigitalOcean Deployment (Easiest Managed Option)

**Time**: 2-3 hours | **Cost**: $150-300/month | **Complexity**: Low

1. Create DO account
2. Create Managed PostgreSQL
3. Create Managed Redis
4. Create Spaces (S3-compatible storage)
5. Deploy with App Platform
6. Configure CDN

**Best for**: Simplest managed deployment, cities with 5,000-50,000 voters

**See**: DEPLOYMENT_GUIDE.md > DigitalOcean section

---

## Maintenance Calendar

### Daily (Automated)
- ✓ Health checks (9 AM)
- ✓ Database backups (2 AM)
- ✓ Redis backups (3 AM)
- ✓ Log rotation
- ✓ Certificate expiry checks

### Weekly (Monday 10 AM)
- Review error logs
- Database vacuum and analyze
- Verify backups
- Security review
- Performance review

### Monthly (First Monday)
- Infrastructure cost review
- Capacity planning
- Security audit
- Dependency updates
- Performance baseline
- Disaster recovery test
- Documentation review

### Quarterly
- Major dependency updates
- Security penetration test
- Full disaster recovery drill
- Architecture review
- Policy updates

---

## Scaling Timeline

### Current: Small City (1K-5K voters)
- 1 backend server (2 vCPU, 4GB RAM)
- 1 database server (2 vCPU, 4GB RAM)
- 1 Redis instance (1GB)
- Cost: ~$100/month

### When to scale:
- CPU > 70% sustained
- Response time > 500ms p95
- Database connections > 80% of pool

### Medium City (5K-25K voters)
- 2 backend servers (2 vCPU, 4GB RAM each)
- 1 database server (4 vCPU, 8GB RAM)
- 1 Redis instance (2GB)
- Add CDN (CloudFront or Cloudflare)
- Cost: ~$300/month

### Large City (25K-100K voters)
- 4 backend servers (4 vCPU, 8GB RAM each)
- 1 database server (8 vCPU, 16GB RAM) + read replica
- Redis cluster (4GB)
- CDN with edge caching
- Load balancer
- Cost: ~$1,500/month

**See**: SCALING_GUIDE.md for detailed scaling procedures

---

## Security Checklist

### Pre-Deployment Security

- [ ] Generate strong SECRET_KEY (32+ characters)
- [ ] Use strong database passwords (32+ characters)
- [ ] Enable 2FA on all service accounts
- [ ] Configure firewall (allow only 80, 443, 22)
- [ ] Set up SSH key authentication (disable password)
- [ ] Configure fail2ban for SSH
- [ ] Enable automatic security updates
- [ ] Set DEBUG=false in production
- [ ] Configure CORS with specific origins
- [ ] Set up SSL/TLS with Let's Encrypt
- [ ] Review all environment variables
- [ ] Set up Sentry for error tracking

### Post-Deployment Security

- [ ] Change all default passwords
- [ ] Test authentication flows
- [ ] Verify rate limiting works
- [ ] Test file upload restrictions
- [ ] Review database permissions
- [ ] Enable audit logging
- [ ] Set up monitoring and alerts
- [ ] Configure automated backups
- [ ] Test backup restoration
- [ ] Review security headers
- [ ] Run security scan (nmap, nikto)
- [ ] Schedule penetration test

### Ongoing Security

- [ ] Weekly log reviews
- [ ] Monthly security audits
- [ ] Quarterly dependency updates
- [ ] Annual penetration test
- [ ] Incident response plan
- [ ] Security awareness training

**See**: SECURITY.md for complete security policy

---

## Support & Resources

### Official Documentation
- Main README: `/README.md`
- API Docs: `https://api.civicq.example.com/docs`
- GitHub: `https://github.com/your-org/civicq`

### Getting Help
1. Check documentation in `/docs`
2. Search GitHub Issues
3. Email: support@civicq.org
4. Emergency: See MONITORING_RUNBOOK.md

### Contributing
- Issues: GitHub Issues
- Pull Requests: See CONTRIBUTING.md
- Security: See SECURITY.md
- Code of Conduct: CODE_OF_CONDUCT.md

---

## Document Status

| Document | Status | Last Updated | Next Review |
|----------|--------|--------------|-------------|
| DEPLOYMENT_GUIDE.md | ✅ Complete | 2026-02-14 | Quarterly |
| OPERATIONS_MANUAL.md | ✅ Complete | 2026-02-14 | Quarterly |
| SCALING_GUIDE.md | ✅ Complete | 2026-02-14 | Quarterly |
| TROUBLESHOOTING_GUIDE.md | ✅ Complete | 2026-02-14 | Quarterly |
| BACKUP_RECOVERY.md | ✅ Complete | 2026-02-14 | Quarterly |
| MONITORING_RUNBOOK.md | 📝 Draft | TBD | Quarterly |
| SECURITY_GUIDE.md | 📝 See SECURITY.md | TBD | Quarterly |
| CITY_ADMIN_GUIDE.md | 📝 See CITY_ONBOARDING.md | TBD | Annually |
| API_DOCUMENTATION.md | 📝 See API_ENDPOINTS.md | TBD | Per release |

---

## Quick Start for Different Roles

### I'm a City IT Administrator
**Start here**: DEPLOYMENT_GUIDE.md
1. Review prerequisites
2. Choose deployment path (VPS recommended for first deployment)
3. Follow step-by-step deployment instructions
4. Complete security checklist
5. Review OPERATIONS_MANUAL.md for ongoing maintenance

### I'm a DevOps Engineer
**Start here**: DEPLOYMENT_GUIDE.md + SCALING_GUIDE.md
1. Review architecture diagrams
2. Choose cloud provider
3. Plan infrastructure (consider growth)
4. Implement auto-scaling
5. Set up monitoring and alerts
6. Configure CI/CD pipelines

### I'm an On-Call Engineer
**Start here**: TROUBLESHOOTING_GUIDE.md + OPERATIONS_MANUAL.md
1. Familiarize yourself with common issues
2. Bookmark quick diagnostic commands
3. Review emergency procedures
4. Test backup restoration
5. Understand escalation paths

### I'm a City Official
**Start here**: CITY_ONBOARDING.md
1. Register your city
2. Complete verification process
3. Import ballot data
4. Set up city staff accounts
5. Configure settings and branding
6. Launch to public

---

## Feedback & Improvements

This documentation is living and should be updated regularly. If you:

- Find errors or outdated information
- Have suggestions for improvement
- Encounter issues not covered
- Successfully deploy using these guides
- Have additional best practices to share

**Please**:
1. Open a GitHub Issue
2. Submit a Pull Request
3. Email: ops@civicq.org

---

**Documentation Version**: 1.0.0
**Last Major Update**: 2026-02-14
**Contributors**: CivicQ Operations Team
**License**: [To be determined]

---

**Built with care for democratic engagement.**
