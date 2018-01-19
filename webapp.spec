# -*- mode: python -*-

block_cipher = None


a = Analysis(['webapp.py'],
             pathex=[],
             binaries=[],
             datas=[('static', 'static'), ('templates', 'templates'), ('bokeh_templates', 'bokeh_templates')],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          name='DARIAH Topics',
          debug=False,
          strip=False,
          upx=False,
          runtime_tmpdir=None,
          console=False,
          icon='static/img/app_icon.ico')
