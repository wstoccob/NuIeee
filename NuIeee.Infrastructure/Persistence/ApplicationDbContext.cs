using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;
using NuIeee.Domain.Entities;

namespace NuIeee.Infrastructure.Persistence;

public class ApplicationDbContext : IdentityDbContext<ApplicationUser, IdentityRole<Guid>, Guid>
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
        AppContext.SetSwitch("Npgsql.EnableLegacyTimestampBehavior", true);
    }

    public DbSet<Team> Teams { get; set; }
    public DbSet<TeamMember> TeamMembers { get; set; }
    public DbSet<Event> Events { get; set; }
    public DbSet<EventPhoto> EventPhotos { get; set; }

    protected override void OnModelCreating(ModelBuilder builder)
    {
        base.OnModelCreating(builder);
        
        // Configure Team-TeamMember relationship
        builder.Entity<Team>()
            .HasMany(t => t.Members)
            .WithOne(m => m.Team)
            .HasForeignKey(m => m.TeamId)
            .OnDelete(DeleteBehavior.Cascade);
        
        builder.Entity<Event>()
            .HasMany(e => e.EventPhotos)
            .WithOne(ep => ep.Event)
            .HasForeignKey(ep => ep.EventId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}
