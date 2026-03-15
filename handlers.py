from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import re
import logging

logger = logging.getLogger(__name__)

def setup_handlers(bot):
    
    # Filter for group chats only (except start command)
    async def group_only(_, __, message: Message):
        return message.chat.type in ["group", "supergroup"]
    
    group_filter = filters.create(group_only)
    
    @bot.app.on_message(filters.command("start") & filters.private)
    async def start_command(client, message: Message):
        """Start command - only works in private"""
        await message.reply_text(
            "🎵 **KERNEL AUDIO BRIDGE BOT** 🎵\n\n"
            "**🔥 Heavy Distortion & Kernel Sound Bridge**\n\n"
            "I can bridge audio between Telegram Voice Chats with **KERNEL-LEVEL PROCESSING**!\n\n"
            "**⚡ Special Kernel Features:**\n"
            "• Multiple kernel presets (Light/Medium/Heavy/Kernel)\n"
            "• Aggressive bass boost\n"
            "• Heavy distortion & saturation\n"
            "• Bit crushing for digital sound\n"
            "• Multi-band compression\n"
            "• Echo with feedback\n\n"
            "**📝 Commands only work in groups!**\n"
            "Add me to a group and use /kernel_help"
        )
    
    @bot.app.on_message(filters.command("kernel_help") & group_filter)
    async def kernel_help_command(client, message: Message):
        """Kernel help command"""
        help_text = """
**🔥 KERNEL AUDIO BRIDGE - HELP 🔥**

**Kernel Presets (Quick Setup):**
/kernel_light - Light distortion
/kernel_medium - Medium aggression
/kernel_heavy - Heavy distortion
/kernel_kernel - ULTIMATE KERNEL SOUND 🔥

**Main Controls:**
/gain <0-500> - Master gain (Default: 200%)
/bass <0-300> - Bass boost (Default: 150%)
/distortion <0-200> - Distortion amount
/saturation <0-200> - Warm saturation
/compression <0-150> - Loudness compression
/loudness <0-150> - Loudness normalization
/echo <0-100> - Echo effect

**Advanced Controls:**
/mid <0-200> - Mid frequencies boost
/treble <0-200> - Treble control
/bitcrush <8-16> - Bit depth reduction
/clip <50-100> - Clipping threshold

**Bridge Commands:**
/join [group_id] - Create audio bridge
/leave - Leave current bridge
/settings - Show current settings
/kernel_status - Show kernel processing status

**💀 For that KERNEL sound, try:**
/kernel_kernel
/gain 400
/bass 300
/distortion 200
/loudness 150
        """
        await message.reply_text(help_text)
    
    @bot.app.on_message(filters.command("kernel_light") & group_filter)
    async def kernel_light(client, message: Message):
        """Set light kernel preset"""
        bot.audio_processor.set_kernel_preset(message.chat.id, 'light')
        await message.reply_text("✅ **Light Kernel Preset Applied**\nBalanced distortion with moderate boost")
    
    @bot.app.on_message(filters.command("kernel_medium") & group_filter)
    async def kernel_medium(client, message: Message):
        """Set medium kernel preset"""
        bot.audio_processor.set_kernel_preset(message.chat.id, 'medium')
        await message.reply_text("✅ **Medium Kernel Preset Applied**\nAggressive sound with good presence")
    
    @bot.app.on_message(filters.command("kernel_heavy") & group_filter)
    async def kernel_heavy(client, message: Message):
        """Set heavy kernel preset"""
        bot.audio_processor.set_kernel_preset(message.chat.id, 'heavy')
        await message.reply_text("✅ **Heavy Kernel Preset Applied**\n🔥 Powerful distortion and heavy bass")
    
    @bot.app.on_message(filters.command("kernel_kernel") & group_filter)
    async def kernel_ultimate(client, message: Message):
        """Set ultimate kernel preset"""
        bot.audio_processor.set_kernel_preset(message.chat.id, 'kernel')
        await message.reply_text(
            "💀 **ULTIMATE KERNEL PRESET APPLIED** 💀\n\n"
            "• Gain: 400%\n"
            "• Bass: 300%\n"
            "• Distortion: 150%\n"
            "• Saturation: 200%\n"
            "• Loudness: 120%\n"
            "• Clip threshold: 150%\n\n"
            "**PREPARE FOR KERNEL LEVEL SOUND!** 🔥"
        )
    
    @bot.app.on_message(filters.command("distortion") & group_filter)
    async def distortion_command(client, message: Message):
        """Adjust distortion"""
        parts = message.text.split()
        if len(parts) != 2:
            await message.reply_text("Usage: `/distortion <0-200>`\nExample: `/distortion 150`")
            return
        
        try:
            value = float(parts[1])
            if value < 0 or value > 200:
                await message.reply_text("❌ Value must be between 0 and 200!")
                return
                
            dist_value = value / 100.0
            bot.audio_processor.set_distortion(message.chat.id, dist_value)
            level = "LIGHT" if value < 50 else "MEDIUM" if value < 100 else "HEAVY" if value < 150 else "KERNEL"
            await message.reply_text(f"✅ Distortion set to **{value}%** ({level})")
        except ValueError:
            await message.reply_text("❌ Invalid value! Please enter a number.")
    
    @bot.app.on_message(filters.command("saturation") & group_filter)
    async def saturation_command(client, message: Message):
        """Adjust saturation"""
        parts = message.text.split()
        if len(parts) != 2:
            await message.reply_text("Usage: `/saturation <0-200>`\nExample: `/saturation 150`")
            return
        
        try:
            value = float(parts[1])
            if value < 0 or value > 200:
                await message.reply_text("❌ Value must be between 0 and 200!")
                return
                
            sat_value = value / 100.0
            bot.audio_processor.set_saturation(message.chat.id, sat_value)
            await message.reply_text(f"✅ Saturation set to **{value}%**")
        except ValueError:
            await message.reply_text("❌ Invalid value! Please enter a number.")
    
    @bot.app.on_message(filters.command("compression") & group_filter)
    async def compression_command(client, message: Message):
        """Adjust compression"""
        parts = message.text.split()
        if len(parts) != 2:
            await message.reply_text("Usage: `/compression <0-150>`\nExample: `/compression 120`")
            return
        
        try:
            value = float(parts[1])
            if value < 0 or value > 150:
                await message.reply_text("❌ Value must be between 0 and 150!")
                return
                
            comp_value = value / 100.0
            bot.audio_processor.set_compression(message.chat.id, comp_value)
            await message.reply_text(f"✅ Compression set to **{value}%**")
        except ValueError:
            await message.reply_text("❌ Invalid value! Please enter a number.")
    
    @bot.app.on_message(filters.command("bass") & group_filter)
    async def bass_command(client, message: Message):
        """Adjust bass"""
        parts = message.text.split()
        if len(parts) != 2:
            await message.reply_text("Usage: `/bass <0-300>`\nExample: `/bass 250`")
            return
        
        try:
            value = float(parts[1])
            if value < 0 or value > 300:
                await message.reply_text("❌ Value must be between 0 and 300!")
                return
                
            bass_value = value / 100.0
            bot.audio_processor.set_bass(message.chat.id, bass_value)
            await message.reply_text(f"✅ Bass boosted to **{value}%**")
        except ValueError:
            await message.reply_text("❌ Invalid value! Please enter a number.")
    
    @bot.app.on_message(filters.command("gain") & group_filter)
    async def gain_command(client, message: Message):
        """Adjust gain"""
        parts = message.text.split()
        if len(parts) != 2:
            await message.reply_text("Usage: `/gain <0-500>`\nExample: `/gain 400`")
            return
        
        try:
            value = float(parts[1])
            if value < 0 or value > 500:
                await message.reply_text("❌ Value must be between 0 and 500!")
                return
                
            gain_value = value / 100.0
            bot.audio_processor.set_gain(message.chat.id, gain_value)
            await message.reply_text(f"✅ Gain set to **{value}%**")
        except ValueError:
            await message.reply_text("❌ Invalid value! Please enter a number.")
    
    @bot.app.on_message(filters.command("loudness") & group_filter)
    async def loudness_command(client, message: Message):
        """Adjust loudness normalization"""
        parts = message.text.split()
        if len(parts) != 2:
            await message.reply_text("Usage: `/loudness <0-150>`\nExample: `/loudness 120`")
            return
        
        try:
            value = float(parts[1])
            if value < 0 or value > 150:
                await message.reply_text("❌ Value must be between 0 and 150!")
                return
                
            loudness_value = value / 100.0
            bot.audio_processor.set_loudness(message.chat.id, loudness_value)
            await message.reply_text(f"✅ Loudness set to **{value}%**")
        except ValueError:
            await message.reply_text("❌ Invalid value! Please enter a number.")
    
    @bot.app.on_message(filters.command("kernel_status") & group_filter)
    async def kernel_status(client, message: Message):
        """Show kernel processing status"""
        settings = bot.audio_processor.get_current_settings(message.chat.id)
        
        if settings:
            # Calculate overall intensity
            intensity = (settings['gain'] * 20 + 
                        settings['bass'] * 30 + 
                        settings['distortion'] * 40 + 
                        settings['saturation'] * 30) / 100
            
            intensity_level = "LIGHT" if intensity < 50 else "MEDIUM" if intensity < 100 else "HEAVY" if intensity < 150 else "KERNEL"
            bars = "█" * min(20, int(intensity / 10)) + "░" * max(0, 20 - min(20, int(intensity / 10)))
            
            text = f"""
**🔥 KERNEL PROCESSING STATUS 🔥**

**Overall Intensity:** {intensity:.1f}%
{bars} {intensity_level}

**⚡ Current Settings:**
├─ Gain: {settings['gain']*100:.0f}%
├─ Bass: {settings['bass']*100:.0f}%
├─ Distortion: {settings['distortion']*100:.0f}%
├─ Saturation: {settings['saturation']*100:.0f}%
├─ Compression: {settings['compression']*100:.0f}%
├─ Loudness: {settings['loudness']*100:.0f}%
└─ Clip: {settings['clip_threshold']*100:.0f}%

**🎛️ EQ Profile:**
{sub_eq(settings['eq'])}

**💀 Kernel Signature:**
{'✅' if intensity > 100 else '❌'} Heavy Distortion
{'✅' if settings['bass'] > 1.5 else '❌'} Deep Bass
{'✅' if settings['saturation'] > 0.8 else '❌'} Warm Saturation
            """
            
            await message.reply_text(text)
        else:
            await message.reply_text("No active session! Use /join first.")
    
    @bot.app.on_message(filters.command("settings") & group_filter)
    async def settings_command(client, message: Message):
        """Show current settings"""
        settings = bot.audio_processor.get_current_settings(message.chat.id)
        
        if settings:
            text = """
**🎵 KERNEL AUDIO SETTINGS** 🎵

**Main Controls:**
├─ Gain: {gain}%
├─ Bass: {bass}%
├─ Distortion: {distortion}%
├─ Saturation: {saturation}%
├─ Compression: {compression}%
├─ Loudness: {loudness}%
└─ Echo: {echo}%

**Quick Presets:**
/kernel_light - /kernel_medium
/kernel_heavy - /kernel_kernel

**For KERNEL sound:**
/kernel_kernel
/gain 400
/bass 300
/distortion 200
            """.format(
                gain=settings['gain']*100,
                bass=settings['bass']*100,
                distortion=settings['distortion']*100,
                saturation=settings['saturation']*100,
                compression=settings['compression']*100,
                loudness=settings['loudness']*100,
                echo=settings['echo']*100
            )
            
            await message.reply_text(text)
        else:
            await message.reply_text("No active session in this chat! Use /join first.")

def sub_eq(eq):
    """Generate EQ visualization"""
    bars = ""
    for val in eq[:5]:  # Show first 5 bands
        bar_len = int(val * 5)
        bars += "█" * bar_len + "░" * (5 - bar_len) + " "
    return bars