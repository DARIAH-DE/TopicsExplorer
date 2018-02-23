# -*- mode: python -*-

block_cipher = None


a = Analysis(['topicsexplorer.py'],
             pathex=[],
             binaries=[],
             datas=[('webapp.py', '.'), ('utils.py', '.'), ('static', 'static'), ('templates', 'templates'), ('bokeh_templates', 'bokeh_templates')],
             hiddenimports=[],
             hookspath=['hooks'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='DARIAH Topics Explorer',
          debug=False,
          strip=False,
          upx=False,
          console=False,
          #icon='static/img/app_icon.png', for macos
          icon='static/img/app_icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='DARIAH Topics Explorer')
