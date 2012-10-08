import os
import rospkg

def get_non_catkin_depends(package, rospack):
    vals = rospack.get_depends(package, implicit=True)
    return [v for v in vals if not rospack.get_manifest(v).is_catkin]

def append_package_paths(manifest, paths, pkg_dir):
    """
    Added paths for package to paths
    :param manifest_: package manifest, ``Manifest``
    :param pkg_dir: package's filesystem directory path, ``str``
    :param paths: list of paths, ``[str]``
    """
    exports = manifest.get_export('python','path')
    if exports:
        for export in exports:
            if ':' in export:
                export = export.split(':')
            else:
                export = [export]
            for e in export:
                paths.append(e.replace('${prefix}', pkg_dir))
    else:
        dirs = [os.path.join(pkg_dir, d) for d in ['src', 'lib']]
        paths.extend([d for d in dirs if os.path.isdir(d)])
    
def generate_python_path(pkg, rospack, m):
    """
    Recursive subroutine for building dependency list and python path
    :raises: :exc:`rospkg.ResourceNotFound` If an error occurs while attempting to load package or dependencies
    """
    # short-circuit if this is a catkin-ized package
    if m.is_catkin:
        return []

    packages = get_non_catkin_depends(pkg, rospack) 
    packages.append(pkg)

    paths = []
    try:
        for p in packages:
            m = rospack.get_manifest(p)
            d = rospack.get_path(p)
            append_package_paths(m, paths, d)
    except:
        raise
    return paths

