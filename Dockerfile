# Use the official .NET SDK image to build and publish the app
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy csproj files and restore as distinct layers
COPY NuIeee.WebApi/NuIeee.WebApi.csproj NuIeee.WebApi/
COPY NuIeee.Application/NuIeee.Application.csproj NuIeee.Application/
COPY NuIeee.Infrastructure/NuIeee.Infrastructure.csproj NuIeee.Infrastructure/
COPY NuIeee.Domain/NuIeee.Domain.csproj NuIeee.Domain/

RUN dotnet restore NuIeee.WebApi/NuIeee.WebApi.csproj

# Copy the rest of the source code
COPY . .

# Build and publish the app
RUN dotnet publish NuIeee.WebApi/NuIeee.WebApi.csproj -c Release -o /app/publish

# Runtime image
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app/publish .

# Expose the default ASP.NET port
EXPOSE 80

# Run the application
ENTRYPOINT ["dotnet", "NuIeee.WebApi.dll"]
