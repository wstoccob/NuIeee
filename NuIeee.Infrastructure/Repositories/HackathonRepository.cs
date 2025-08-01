using Microsoft.EntityFrameworkCore;
using NuIeee.Application.DTOs.Hackathon;
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

    public async Task<List<HackathonTeamDto>> GetHackathonTeamsAsync(CancellationToken cancellationToken)
    {
        var teams = await _context.Teams
            .Include(t => t.Members)
            .ToListAsync(cancellationToken);
        
        return teams.Select(team => new HackathonTeamDto
        {
            TeamName = team.Name,
            Members = team.Members.Select(m => new TeamMemberDto
            {
                FullName = m.FullName,
                NuId = m.NuId,
                Iin = m.Iin,
                Email = m.Email,
                YearOfStudy = m.YearOfStudy,
                Major = m.Major
            }).ToList()
        }).ToList();
    }
}