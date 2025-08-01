using MediatR;
using NuIeee.Application.DTOs.Hackathon;

namespace NuIeee.Application.Features.Hackathon;

public record GetHackathonTeamsQuery() : IRequest<List<HackathonTeamDto>>;