import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import crawler


def test_prompt_before_baixar_click():
    events = []
    driver = MagicMock()
    driver.window_handles = ['main', 'new']
    driver.current_window_handle = 'main'
    driver.switch_to.window.side_effect = lambda handle: events.append('switch')

    with patch('crawler.WebDriverWait') as MockWait, \
         patch('crawler.close_certificate_popup') as mock_close, \
         patch('crawler.wait_for_user', side_effect=lambda msg='': events.append(msg)):
        element_acesso = MagicMock()
        element_baixar = MagicMock()
        element_acesso.click.side_effect = lambda: events.append('click_acesso')
        element_baixar.click.side_effect = lambda: events.append('click_baixar')

        MockWait.return_value.until.side_effect = [element_acesso, element_baixar]
        crawler.navigate_to_download_page(driver)

        assert mock_close.called

    assert 'Complete any required authentication, then continue...' in events
    assert 'Complete any additional authentication, then press Enter...' in events
    assert events.index('Complete any required authentication, then continue...') < events.index('click_baixar')
