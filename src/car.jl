import Pkg; Pkg.activate(joinpath(@__DIR__,"..")); Pkg.instantiate()
using RobotZoo
using RobotZoo: BicycleModel
using JLD2
using FileIO
using RobotDynamics
using LinearAlgebra
using StaticArrays
using Colors
using MeshCat
using GeometryBasics
using CoordinateTransformations
using Rotations
const TRAJFILE = joinpath(@__DIR__, "parallel_park.jld2")

##
"""
    set_mesh!(vis, model::BicycleModel)
    
Add a simple model of the bicycle model to the MeshCat visualizer `vis`
"""
function set_mesh!(vis, model::RobotZoo.BicycleModel)
    L, lr = model.L,  model.lr
    lf = L - lr
    ww = 0.23     # wheel width (m)
    r = 0.3       # wheel radius (m)
    bw = 0.1      # chassis width (m)
    wheel = Cylinder(Point3f0(0,-ww/2,0), Point3f0(0,ww/2,0), Float32(r))
    body = Rect3D(Vec(0,-bw/2,-bw/2), Vec(L,bw,bw))
    setobject!(vis["geom"], Triad()) 
    setobject!(vis["geom"]["chassis"]["body"], body, MeshPhongMaterial(color=colorant"gray"))
    setobject!(vis["geom"]["chassis"]["wheel"], wheel, MeshPhongMaterial(color=colorant"black"))
    setobject!(vis["geom"]["front"]["wheel"], wheel, MeshPhongMaterial(color=colorant"black"))
    if model.ref == :rear
        settransform!(vis["geom"]["front"], compose(Translation(L,0,0)))
        settransform!(vis["geom"]["chassis"], compose(Translation(0,0,0)))
    elseif model.ref == :front
        settransform!(vis["geom"]["front"], compose(Translation(0,0,0)))
        settransform!(vis["geom"]["chassis"], compose(Translation(-L,0,0)))
    elseif model.ref == :cg
        settransform!(vis["geom"]["front"], compose(Translation(lf,0,0)))
        settransform!(vis["geom"]["chassis"], compose(Translation(-lr,0,0)))
    end
    settransform!(vis["geom"], Translation(0,0,r))
end

"""
    visualize!(vis, model, x)

Visualize a single frame of `model` given the state vector `x`.
"""
function visualize!(vis, model::RobotZoo.BicycleModel, x::StaticVector)
    θ = x[3]
    δ = x[4]
    settransform!(vis["robot"]["geom"], compose(Translation(x[1], x[2],0), LinearMap(RotZ(θ))))
    settransform!(vis["robot"]["geom"]["front"]["wheel"], LinearMap(RotZ(δ)))
end

"""
    visualize!(vis, model, tf, X)

Visualize a trajectory for `model` give the total time `tf` and a trajectory of states `X`.
"""
function visualize!(vis, model::BicycleModel, tf::Real, X)
    fps = Int(round((length(X)-1)/tf))
    anim = MeshCat.Animation(fps)
    for (k,x) in enumerate(X)
        atframe(anim, k) do
            x = X[k]
            visualize!(vis, model, SA[x[1], x[2], x[3], x[4]])
        end
    end
    setanimation!(vis, anim)
end

"""
    initialize_visualizer(model)

Launch a MeshCat visualizer and insert the geometry for `model`.
"""
function initialize_visualizer(model::BicycleModel)
    vis = Visualizer()
    set_mesh!(vis["robot"], model)
    render(vis)
    return vis
end

"""
    plot_region!(vis, Δx, Δy; [origin, color])

Plot a rectangular region of width `2Δx` and height `2Δy`, centered at `origin` (default `(0,0)`) in
the MeshCat visualizer `vis`. The color can be changed via the `color` keyword argument.
"""
function plot_region!(vis, Δx, Δy, origin=(0,0), color=colorant"rgba(0,255,0,0.5)")
    box = Rect3D(Point3f0(-Δx+origin[1],-Δy+origin[2],-0.1), Point3f0(2Δx,2Δy,0.1))
    setobject!(vis["ic"], box, MeshPhongMaterial(color=color))
end