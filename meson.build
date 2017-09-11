project('gnome-workflowy', version: '0.0.1')

project_id = 'io.mspencer.Workflowy'

python = import('python3')
gnome = import('gnome')

message('Looking for dependencies')
python_bin = python.find_python()
if not python_bin.found()
  error('No valid python3 binary found')
else
  message('Found python3 binary')
endif
glib = dependency('glib-2.0')
dependency('gobject-introspection-1.0')
gtk = dependency('gtk+-3.0')

python_dir = join_paths(get_option('prefix'), python.sysconfig_path('purelib'))
bindir = join_paths(get_option('prefix'), get_option('bindir'))
DATA_DIR = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())

conf = configuration_data()
conf.set('VERSION', meson.project_version())
conf.set('DATA_DIR', DATA_DIR)
conf.set('PYTHON', python_bin.path())

subdir('data')

install_subdir('workflowy', install_dir: python_dir)

configure_file(input: 'gnome-workflowy.in', output: 'gnome-workflowy', configuration: conf, install_dir: bindir)
