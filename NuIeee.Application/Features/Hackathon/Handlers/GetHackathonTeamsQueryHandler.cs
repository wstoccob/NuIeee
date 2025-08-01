using MediatR;
using NuIeee.Application.DTOs.Hackathon;
using NuIeee.Application.Interfaces;

namespace NuIeee.Application.Features.Hackathon.Handlers;

public class GetHackathonTeamsQueryHandler(IHackathonRepository hackathonRepository) : IRequestHandler<GetHackathonTeamsQuery, List<HackathonTeamDto>>
{
    
    public async Task<List<HackathonTeamDto>> Handle(GetHackathonTeamsQuery request, CancellationToken cancellationToken)
    {
        return await hackathonRepository.GetHackathonTeamsAsync(cancellationToken);
    }
}