using NuIeee.Application.Interfaces;
using NuIeee.Domain.Entities;
using NuIeee.Infrastructure.Persistence;

namespace NuIeee.Infrastructure.Repositories;

public class HackathonRepository : IHackathonRepository
{
    private readonly ApplicationDbContext _context;

    public HackathonRepository(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task AddTeamAsync(Team team, CancellationToken cancellationToken)
    {
        await _context.Teams.AddAsync(team, cancellationToken);
        await _context.SaveChangesAsync(cancellationToken);
    }
}